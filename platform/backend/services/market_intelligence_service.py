"""
Service for Market Intelligence Distillation using SLMs (Connectionist Intelligence)
"""

import json
import logging
import os
from typing import Dict, Any, List

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

logger = logging.getLogger(__name__)

class MarketIntelligenceService:
    """
    Analyzes unstructured market data (simulated inputs) to extract structured metrics
    for Resale and Maintenance agents.
    """

    SYSTEM_PROMPT = """
    You are an expert Automotive Market Analyst.
    Analyze the provided text (news, reviews, forum discussions) and extract key metrics for the specific car model mentioned.
    
    Output JSON ONLY.
    Fields:
    - 'sentiment_score': -1.0 (Very Negative) to 1.0 (Very Positive).
    - 'reliability_impact': -0.5 (Major Issues) to +0.2 (Very Reliable).
    - 'resale_factor': 0.8 (Depreciates fast) to 1.2 (Holds value well).
    - 'common_issues': List[str] (Max 3 keywords).
    
    Example: {"sentiment_score": -0.4, "reliability_impact": -0.3, "resale_factor": 0.9, "common_issues": ["transmission", "overheating"]}
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
        
        # In-memory knowledge base (Simulating a database/cache)
        self.knowledge_base = {} 

    def analyze_market_text(self, car_model: str, text: str) -> Dict[str, Any]:
        """
        Analyzes text to update knowledge base for a car model.
        """
        prompt = f"Car Model: {car_model}\nMarket Text: {text}"
        
        result = {}
        # Try Primary
        if self.primary_client:
            try:
                response = self._call_llm(self.primary_client, self.primary_model, prompt)
                result = self._parse_json_response(response)
            except Exception as e:
                logger.warning(f"Primary SLM failed: {e}")

        # Try Fallback if primary failed
        if not result and self.fallback_client:
            try:
                response = self._call_llm(self.fallback_client, self.fallback_model, prompt)
                result = self._parse_json_response(response)
            except Exception as e:
                logger.warning(f"Fallback SLM failed: {e}")

        if result:
            self._update_knowledge_base(car_model, result)
            
        return result

    def get_market_metrics(self, car_model: str) -> Dict[str, Any]:
        """Returns cached metrics for a model."""
        return self.knowledge_base.get(car_model, {})

    def _update_knowledge_base(self, car_model: str, metrics: Dict[str, Any]):
        """Updates the internal KB combining old and new data (Simple Override for now)."""
        self.knowledge_base[car_model] = metrics
        # In production this would persist to disk/DB

    def _call_llm(self, client, model: str, prompt: str) -> str:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=model,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return chat_completion.choices[0].message.content

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except Exception:
            return {}
