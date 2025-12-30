"""
Serviço de Justificativas usando LLM
Fase 1: Groq Llama (primário) + OpenAI (fallback) + Templates (fallback final)

Estratégia de 3 níveis:
1. Groq + Llama 3.1 8B (primário): Grátis, rápido (~200-400ms), 95% qualidade
2. OpenAI GPT-4o-mini (fallback): Pago, boa qualidade, caso Groq falhe
3. Templates (fallback final): Sempre funciona, baseado em regras
"""

from typing import Dict, Optional
import os
import time
import logging
import re

# Imports opcionais (graceful degradation)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("⚠️ Groq SDK não instalado. Instale com: pip install groq")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("⚠️ OpenAI SDK não instalado. Instale com: pip install openai")

from models.car import Car
from models.user_profile import UserProfile
from services.llm_prompts import (
    SYSTEM_PROMPT_DIDATICO,
    USER_PROMPT_TEMPLATE,
    get_context_hint,
    build_prioridades_string,
    format_safety_features,
    format_comfort_features,
    get_financial_health_description
)

# Configurar logging
logger = logging.getLogger(__name__)


class LLMJustificationService:
    """
    Serviço para geração de justificativas usando LLM

    Arquitetura de fallback em 3 níveis:
    1. Groq Llama 3.1 8B (primário)
    2. OpenAI GPT-4o-mini (fallback)
    3. Templates (fallback final)
    """

    def __init__(
        self,
        primary_provider: str = "groq",
        primary_model: str = "llama-3.1-8b-instant",
        fallback_provider: str = "openai",
        fallback_model: str = "gpt-4o-mini",
        enable_cache: bool = True
    ):
        """
        Inicializa serviço de justificativas LLM

        Args:
            primary_provider: Provedor primário ('groq')
            primary_model: Modelo primário ('llama-3.1-8b-instant')
            fallback_provider: Provedor de fallback ('openai')
            fallback_model: Modelo de fallback ('gpt-4o-mini')
            enable_cache: Habilita cache de respostas (futuro)
        """
        self.enable_cache = enable_cache

        # === NÍVEL 1: Groq + Llama (Primário) ===
        self.primary_provider = primary_provider
        self.primary_model = primary_model
        self.primary_client = None

        if primary_provider == "groq" and GROQ_AVAILABLE:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                try:
                    self.primary_client = Groq(api_key=groq_api_key)
                    logger.info(f"✅ Provedor primário habilitado: Groq {primary_model}")
                except Exception as e:
                    logger.error(f"❌ Erro ao inicializar Groq: {e}")
            else:
                logger.warning("⚠️ GROQ_API_KEY não configurada")

        # === NÍVEL 2: OpenAI GPT-4o-mini (Fallback) ===
        self.fallback_provider = fallback_provider
        self.fallback_model = fallback_model
        self.fallback_client = None

        if fallback_provider == "openai" and OPENAI_AVAILABLE:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    self.fallback_client = OpenAI(api_key=openai_api_key)
                    logger.info(f"✅ Fallback habilitado: OpenAI {fallback_model}")
                except Exception as e:
                    logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
            else:
                logger.warning("⚠️ OPENAI_API_KEY não configurada")

        # Métricas de uso
        self.metrics = {
            "total_calls": 0,
            "primary_calls": 0,
            "primary_success": 0,
            "fallback_calls": 0,
            "fallback_success": 0,
            "template_fallback": 0,
            "total_latency_primary": 0.0,
            "total_latency_fallback": 0.0,
        }

        # Log status inicial
        if not self.primary_client and not self.fallback_client:
            logger.warning(
                "⚠️ Nenhum provedor LLM disponível. "
                "Usando apenas templates."
            )

    def generate_justification(
        self,
        car: Car,
        profile: UserProfile,
        score: float,
        position: int,
        total_results: int,
        tco_breakdown: Dict,
        other_cars: Optional[list] = None
    ) -> str:
        """
        Gera justificativa contextual para uma recomendação

        Args:
            car: Carro recomendado
            profile: Perfil do usuário
            score: Score final do matching (0-1)
            position: Posição no ranking (1-based)
            total_results: Total de resultados
            tco_breakdown: Detalhamento do TCO
            other_cars: Outros carros no ranking (para comparação futura)

        Returns:
            Justificativa em português (2-3 frases, 150-300 caracteres)
        """
        self.metrics["total_calls"] += 1

        # Construir prompt uma vez
        prompt = self._build_prompt(
            car, profile, score, position, total_results, tco_breakdown
        )

        # === NÍVEL 1: Tentar Groq + Llama (primário) ===
        if self.primary_client:
            try:
                start_time = time.time()
                result = self._call_groq(prompt)
                latency = time.time() - start_time

                if self._validate_output(result):
                    self.metrics["primary_calls"] += 1
                    self.metrics["primary_success"] += 1
                    self.metrics["total_latency_primary"] += latency

                    logger.debug(
                        f"✅ Justificativa via Groq ({latency:.2f}s) "
                        f"para {car.nome}"
                    )
                    return self._simplify_text(result)

            except Exception as e:
                self.metrics["primary_calls"] += 1
                logger.warning(
                    f"❌ Groq falhou para {car.nome}: {e}",
                    extra={"car_id": car.id, "error": str(e)}
                )

        # === NÍVEL 2: Tentar OpenAI (fallback) ===
        if self.fallback_client:
            try:
                start_time = time.time()
                result = self._call_openai(prompt)
                latency = time.time() - start_time

                if self._validate_output(result):
                    self.metrics["fallback_calls"] += 1
                    self.metrics["fallback_success"] += 1
                    self.metrics["total_latency_fallback"] += latency

                    logger.info(
                        f"✅ Justificativa via OpenAI fallback ({latency:.2f}s) "
                        f"para {car.nome}"
                    )
                    return self._simplify_text(result)

            except Exception as e:
                self.metrics["fallback_calls"] += 1
                logger.warning(
                    f"❌ OpenAI fallback falhou para {car.nome}: {e}",
                    extra={"car_id": car.id, "error": str(e)}
                )

        # === NÍVEL 3: Fallback para templates ===
        logger.info(f"⚠️ Usando template fallback para {car.nome}")
        self.metrics["template_fallback"] += 1
        return self._generate_template_fallback(car, profile, score, tco_breakdown)

    def _build_prompt(
        self,
        car: Car,
        profile: UserProfile,
        score: float,
        position: int,
        total_results: int,
        tco_breakdown: Dict
    ) -> str:
        """
        Constrói prompt otimizado para o LLM

        Args:
            car: Carro recomendado
            profile: Perfil do usuário
            score: Score de matching
            position: Posição no ranking
            total_results: Total de resultados
            tco_breakdown: Breakdown do TCO

        Returns:
            Prompt formatado
        """
        # Extrair informações do carro
        car_nome = car.nome
        car_preco = car.preco
        car_categoria = car.categoria or "Não especificada"
        car_ano = car.ano or "N/A"
        car_consumo_cidade = getattr(car, 'consumo_cidade', 'N/A')
        car_consumo_estrada = getattr(car, 'consumo_estrada', 'N/A')

        # Formatar itens de segurança e conforto
        car_seguranca = format_safety_features(
            getattr(car, 'itens_seguranca', [])
        )
        car_conforto = format_comfort_features(
            getattr(car, 'itens_conforto', [])
        )

        # Informações da concessionária
        dealership_nome = getattr(car, 'dealership_nome', 'Concessionária')
        dealership_cidade = getattr(car, 'dealership_cidade', 'São Paulo')

        # Extrair informações do perfil
        uso_principal = profile.uso_principal
        tamanho_familia = profile.tamanho_familia
        tem_criancas = "Sim" if getattr(profile, 'tem_criancas', False) else "Não"
        orcamento_min = profile.orcamento_min
        orcamento_max = profile.orcamento_max

        # Prioridades formatadas
        prioridades_str = build_prioridades_string(
            getattr(profile, 'prioridades', {})
        )

        # Renda mensal (pode não estar informada)
        renda_mensal = getattr(profile, 'renda_mensal', 0)
        if renda_mensal == 0:
            renda_mensal_str = "não informada"
        else:
            renda_mensal_str = f"R$ {renda_mensal:,.2f}"

        # Análise do matching
        score_percent = int(score * 100)
        tco_mensal = tco_breakdown.get('total_mensal', 0)
        tco_percent = int((tco_mensal / renda_mensal * 100)) if renda_mensal > 0 else 0

        # Top features (simplificado)
        top_features = "Adequação ao uso, custo-benefício"
        if score >= 0.85:
            top_features = "Excelente compatibilidade com suas necessidades"
        elif score >= 0.70:
            top_features = "Boa compatibilidade com o que você procura"

        # Context hint baseado no uso
        context_hint = get_context_hint(uso_principal)

        # Montar prompt
        prompt = USER_PROMPT_TEMPLATE.format(
            car_nome=car_nome,
            car_preco=car_preco,
            car_categoria=car_categoria,
            car_ano=car_ano,
            car_consumo_cidade=car_consumo_cidade,
            car_consumo_estrada=car_consumo_estrada,
            car_seguranca=car_seguranca,
            car_conforto=car_conforto,
            dealership_nome=dealership_nome,
            dealership_cidade=dealership_cidade,
            uso_principal=uso_principal,
            tamanho_familia=tamanho_familia,
            tem_criancas=tem_criancas,
            orcamento_min=orcamento_min,
            orcamento_max=orcamento_max,
            prioridades_str=prioridades_str,
            renda_mensal=renda_mensal_str,
            score_percent=score_percent,
            position=position,
            total_results=total_results,
            tco_mensal=tco_mensal,
            tco_percent=tco_percent,
            top_features=top_features,
            context_hint=context_hint
        )

        return prompt

    def _call_groq(self, prompt: str, timeout: int = 8) -> str:
        """
        Chama Groq com Llama como provedor primário

        Args:
            prompt: Prompt do usuário
            timeout: Timeout em segundos

        Returns:
            Texto gerado pelo LLM
        """
        response = self.primary_client.chat.completions.create(
            model=self.primary_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_DIDATICO},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7,
            timeout=timeout
        )

        return response.choices[0].message.content.strip()

    def _call_openai(self, prompt: str, timeout: int = 10) -> str:
        """
        Chama OpenAI como fallback

        Args:
            prompt: Prompt do usuário
            timeout: Timeout em segundos

        Returns:
            Texto gerado pelo LLM
        """
        response = self.fallback_client.chat.completions.create(
            model=self.fallback_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_DIDATICO},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7,
            timeout=timeout
        )

        return response.choices[0].message.content.strip()

    def _validate_output(self, text: str) -> bool:
        """
        Valida se output do LLM é adequado

        Args:
            text: Texto gerado

        Returns:
            True se válido, False caso contrário
        """
        if not text or not text.strip():
            logger.debug("❌ Output vazio")
            return False

        text_len = len(text)

        if text_len < 50:
            logger.debug(f"❌ Output muito curto: {text_len} chars")
            return False

        if text_len > 600:
            logger.debug(f"⚠️ Output muito longo: {text_len} chars")
            # Aceita mas vai truncar

        return True

    def _simplify_text(self, text: str) -> str:
        """
        Pós-processa texto do LLM para garantir linguagem acessível

        Substitui siglas técnicas que podem ter escapado do prompt

        Args:
            text: Texto original do LLM

        Returns:
            Texto simplificado
        """
        # Substituir siglas comuns
        replacements = {
            r'\bTCO\b': 'custo mensal total',
            r'\bISOFIX\b': 'pontos de fixação para cadeirinha',
            r'\bABS\b': 'freios de segurança',
            r'\bESP\b': 'controle de estabilidade',
            r'\bESC\b': 'controle de estabilidade',
        }

        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Truncar se muito longo
        if len(result) > 500:
            result = result[:497] + "..."

        return result

    def _generate_template_fallback(
        self,
        car: Car,
        profile: UserProfile,
        score: float,
        tco_breakdown: Dict
    ) -> str:
        """
        Fallback final usando templates (código atual)
        Com linguagem didática

        Args:
            car: Carro recomendado
            profile: Perfil do usuário
            score: Score de matching
            tco_breakdown: Breakdown do TCO

        Returns:
            Justificativa template em português claro
        """
        parts = []

        # 1. Adequação ao uso (em linguagem simples)
        uso_descriptions = {
            "familia": f"Ótima opção para sua família de {profile.tamanho_familia} pessoas",
            "trabalho": "Ideal para o dia a dia de trabalho",
            "comercial": "Adequado para uso comercial e entregas",
            "primeiro_carro": "Excelente escolha para quem está começando",
            "lazer": "Perfeito para passeios e viagens",
            "transporte_passageiros": "Aprovado para trabalhar com apps de transporte"
        }

        uso_desc = uso_descriptions.get(
            profile.uso_principal,
            "Boa opção para suas necessidades"
        )
        parts.append(uso_desc)

        # 2. Destaque financeiro (em reais, não percentual)
        tco_mensal = tco_breakdown.get("total_mensal", 0)
        if tco_mensal > 0:
            financial_desc = get_financial_health_description(
                tco_breakdown.get("budget_percentage", 30)
            )
            parts.append(
                f"com custo mensal de R$ {tco_mensal:,.0f} "
                f"(incluindo tudo: parcela, gasolina, manutenção) - "
                f"{financial_desc}"
            )

        # 3. Destaque de compatibilidade
        if score >= 0.85:
            parts.append("Alta compatibilidade com o que você procura")
        elif score >= 0.70:
            parts.append("Atende bem suas necessidades")

        return ". ".join(parts) + "."

    def get_metrics(self) -> Dict:
        """
        Retorna métricas de uso do serviço

        Returns:
            Dict com métricas agregadas
        """
        total_calls = self.metrics["total_calls"]

        if total_calls == 0:
            return {
                "total_calls": 0,
                "primary_success_rate": 0.0,
                "fallback_usage_rate": 0.0,
                "template_usage_rate": 0.0,
                "avg_latency_primary": 0.0,
                "avg_latency_fallback": 0.0
            }

        primary_calls = self.metrics["primary_calls"]
        fallback_calls = self.metrics["fallback_calls"]

        return {
            "total_calls": total_calls,
            "primary_success_rate": (
                self.metrics["primary_success"] / primary_calls
                if primary_calls > 0 else 0.0
            ),
            "fallback_usage_rate": fallback_calls / total_calls,
            "fallback_success_rate": (
                self.metrics["fallback_success"] / fallback_calls
                if fallback_calls > 0 else 0.0
            ),
            "template_usage_rate": self.metrics["template_fallback"] / total_calls,
            "avg_latency_primary": (
                self.metrics["total_latency_primary"] / self.metrics["primary_success"]
                if self.metrics["primary_success"] > 0 else 0.0
            ),
            "avg_latency_fallback": (
                self.metrics["total_latency_fallback"] / self.metrics["fallback_success"]
                if self.metrics["fallback_success"] > 0 else 0.0
            )
        }
