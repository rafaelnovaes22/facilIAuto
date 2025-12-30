"""
Service for Semantic Analysis of User Profiles using SLMs (Connectionist Intelligence)
"""

import json
import logging
import os
from typing import Dict, Any, Optional

# Reusing providers setup from LLMJustificationService structure logic
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from models.user_profile import UserProfile

logger = logging.getLogger(__name__)

class SemanticAnalysisService:
    """
    Analyzes user profiles and unstructured text to infer hidden preferences/weights using SLMs.
    Output is a vector of weight adjustments (semantic_weights).
    """

    SYSTEM_PROMPT = """
    You are an expert Car Buyer Psychologist. 
    Analyze the user profile and output a JSON object with weight adjustments (-0.2 to +0.2).
    
    The weights are: 
    - 'economy': Fuel efficiency and low maintenance.
    - 'comfort': Ride quality, noise isolation, features.
    - 'performance': Acceleration, handling, power.
    - 'reliability': Durability, low breakdown risk.
    - 'safety': Crash test ratings, airbags, ADAS.
    - 'resale': Value retention.
    - 'space': Cargo and passenger volume.
    
    Output ONLY valid JSON. No markdown, no explanations.
    Example: {"economy": 0.1, "comfort": -0.05, "performance": 0.0, "reliability": 0.2, "safety": 0.15, "resale": 0.0, "space": 0.1}
    """

    def __init__(
        self,
        primary_provider: str = "groq",
        primary_model: str = "llama-3.1-8b-instant",
        fallback_provider: str = "openai",
        fallback_model: str = "gpt-4o-mini"
    ):
        self.primary_client = None
        self.fallback_client = None
        self.primary_model = primary_model
        self.fallback_model = fallback_model

        # Initialize clients (similar to LLMJustificationService)
        if primary_provider == "groq" and GROQ_AVAILABLE:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.primary_client = Groq(api_key=api_key)
                except Exception as e:
                    logger.error(f"Failed to init Groq: {e}")

        if fallback_provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.fallback_client = OpenAI(api_key=api_key)
                except Exception as e:
                    logger.error(f"Failed to init OpenAI: {e}")

    def analyze_profile(self, profile: UserProfile) -> Dict[str, float]:
        """
        Analyzes the structured profile to infer implicit weights.
        """
        prompt = self._build_profile_prompt(profile)
        
        # Try Primary
        if self.primary_client:
            try:
                response = self._call_llm(self.primary_client, self.primary_model, prompt)
                return self._parse_json_response(response)
            except Exception as e:
                logger.warning(f"Primary SLM failed: {e}")

        # Try Fallback
        if self.fallback_client:
            try:
                response = self._call_llm(self.fallback_client, self.fallback_model, prompt)
                return self._parse_json_response(response)
            except Exception as e:
                logger.warning(f"Fallback SLM failed: {e}")

        # Final Fallback: Return neutral adjustment
        return self._heuristic_fallback(profile)

    def _build_profile_prompt(self, profile: UserProfile) -> str:
        """Converts profile to a descriptive narrative for the SLM."""
        return f"""
        User Profile Analysis:
        - Primary Use: {profile.uso_principal}
        - Family Size: {profile.tamanho_familia}
        - Has Children: {getattr(profile, 'tem_criancas', False)}
        - Budget: R$ {profile.orcamento_min} - R$ {profile.orcamento_max}
        - Stated Priorities: {profile.prioridades}
        - First Car: {getattr(profile, 'primeiro_carro', False)}
        - Daily Commute: {getattr(profile, 'km_diario', 'Unknown')} km
        
        Infer the hidden psychological priorities and risk aversions.
        """

    def _call_llm(self, client, model: str, prompt: str) -> str:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=model,
            temperature=0.3, # Low temp for structured output
            response_format={"type": "json_object"}, # Force JSON if supported
        )
        return chat_completion.choices[0].message.content

    def _parse_json_response(self, text: str) -> Dict[str, float]:
        try:
            data = json.loads(text)
            # Validate keys and value ranges
            valid_keys = {'economy', 'comfort', 'performance', 'reliability', 'safety', 'resale', 'space'}
            clean_data = {}
            for k, v in data.items():
                if k in valid_keys and isinstance(v, (int, float)):
                    # Clamp values to safe range -0.5 to +0.5 to prevent extreme skews
                    clean_data[k] = max(-0.5, min(0.5, float(v)))
            return clean_data
        except Exception:
            return {}

    def _heuristic_fallback(self, profile: UserProfile) -> Dict[str, float]:
        """Simple rules if SLM fails."""
        weights = {}
        if profile.uso_principal == 'familia':
            weights['safety'] = 0.1
            weights['space'] = 0.1
        elif profile.uso_principal == 'trabalho':
            weights['economy'] = 0.1
            weights['reliability'] = 0.1
        return weights
