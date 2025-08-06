"""
Processador Avançado de Preferências de Marca/Modelo
Integra fuzzy matching e validação inteligente no backend
"""

import logging
from typing import Dict, List, Optional, Tuple

from app.brand_matcher import brand_matcher
from app.models import QuestionarioBusca

logger = logging.getLogger(__name__)


class EnhancedBrandProcessor:
    """Processador que aplica a pesquisa detalhada de coleta de preferências"""

    def __init__(self):
        self.matcher = brand_matcher

    def process_and_validate_preferences(
        self, questionario: QuestionarioBusca
    ) -> Dict[str, any]:
        """
        Aplica validação e normalização avançada das preferências
        Baseado na pesquisa de estruturação de coleta de preferências
        """
        try:
            # 1. Validação e Normalização da Marca Principal
            marca_result = self.matcher.validate_and_normalize_preferences(
                questionario.marca_preferida, questionario.modelo_especifico
            )

            # 2. Processamento de Marcas Alternativas
            marcas_alternativas_processadas = []
            if (
                hasattr(questionario, "marcas_alternativas")
                and questionario.marcas_alternativas
            ):
                for marca_alt in questionario.marcas_alternativas:
                    marca_alt_result = self.matcher.find_best_brand_match(marca_alt)
                    if marca_alt_result.confidence >= 0.6:
                        marcas_alternativas_processadas.append(
                            {
                                "original": marca_alt,
                                "normalizada": marca_alt_result.matched,
                                "confianca": marca_alt_result.confidence,
                            }
                        )

            # 3. Processamento de Modelos Alternativos
            modelos_alternativos_processados = []
            if (
                hasattr(questionario, "modelos_alternativos")
                and questionario.modelos_alternativos
            ):
                marca_para_modelo = marca_result.get("marca_normalizada", "")
                for modelo_alt in questionario.modelos_alternativos:
                    modelo_alt_result = self.matcher.find_best_model_match(
                        modelo_alt, marca_para_modelo
                    )
                    if modelo_alt_result.confidence >= 0.6:
                        modelos_alternativos_processados.append(
                            {
                                "original": modelo_alt,
                                "normalizado": modelo_alt_result.matched,
                                "confianca": modelo_alt_result.confidence,
                            }
                        )

            # 4. Estratégias para Respostas Vagas ou Conflitantes
            validation_issues = []
            confidence_score = 0.0

            # Verificar qualidade da marca principal
            if marca_result["marca_confianca"] < 0.8:
                validation_issues.append(
                    {
                        "type": "low_confidence_brand",
                        "message": f"Marca '{questionario.marca_preferida}' tem baixa confiança ({marca_result['marca_confianca']:.2f})",
                        "suggestions": marca_result["marca_sugestoes"],
                    }
                )
            else:
                confidence_score += 0.4

            # Verificar qualidade do modelo
            if (
                marca_result["modelo_confianca"] < 0.8
                and questionario.modelo_especifico != "aberto_opcoes"
            ):
                validation_issues.append(
                    {
                        "type": "low_confidence_model",
                        "message": f"Modelo '{questionario.modelo_especifico}' tem baixa confiança ({marca_result['modelo_confianca']:.2f})",
                        "suggestions": marca_result["modelo_sugestoes"],
                    }
                )
            else:
                confidence_score += 0.3

            # Verificar conflitos entre marca principal e alternativas
            marca_principal = marca_result.get("marca_normalizada", "").upper()
            for marca_alt in marcas_alternativas_processadas:
                if marca_alt["normalizada"].upper() == marca_principal:
                    validation_issues.append(
                        {
                            "type": "conflicting_preferences",
                            "message": f"Marca '{marca_alt['original']}' está duplicada entre principal e alternativas",
                        }
                    )

            # Pontuação adicional por completude
            if marcas_alternativas_processadas:
                confidence_score += 0.15
            if modelos_alternativos_processados:
                confidence_score += 0.15

            # 5. Resultado Estruturado
            result = {
                "marca_principal": {
                    "original": questionario.marca_preferida,
                    "normalizada": marca_result["marca_normalizada"],
                    "confianca": marca_result["marca_confianca"],
                    "sugestoes": marca_result["marca_sugestoes"],
                },
                "modelo_principal": {
                    "original": questionario.modelo_especifico,
                    "normalizado": marca_result["modelo_normalizado"],
                    "confianca": marca_result["modelo_confianca"],
                    "sugestoes": marca_result["modelo_sugestoes"],
                },
                "marcas_alternativas": marcas_alternativas_processadas,
                "modelos_alternativos": modelos_alternativos_processados,
                "validation_issues": validation_issues,
                "confidence_score": min(confidence_score, 1.0),
                "needs_user_confirmation": len(validation_issues) > 0
                or confidence_score < 0.7,
                "processing_quality": self._assess_processing_quality(
                    confidence_score, validation_issues
                ),
            }

            logger.info(
                f"Preferências processadas - Confiança: {confidence_score:.2f}, Issues: {len(validation_issues)}"
            )
            return result

        except Exception as e:
            logger.error(f"Erro ao processar preferências: {e}")
            return {
                "error": str(e),
                "fallback_result": True,
                "marca_principal": {"normalizada": questionario.marca_preferida},
                "modelo_principal": {"normalizado": questionario.modelo_especifico},
            }

    def _assess_processing_quality(
        self, confidence_score: float, issues: List[Dict]
    ) -> str:
        """Avalia a qualidade do processamento"""
        if confidence_score >= 0.9 and len(issues) == 0:
            return "excellent"
        elif confidence_score >= 0.7 and len(issues) <= 1:
            return "good"
        elif confidence_score >= 0.5:
            return "fair"
        else:
            return "poor"

    def generate_improvement_suggestions(self, processing_result: Dict) -> List[str]:
        """
        Gera sugestões para melhorar a qualidade das preferências
        Implementa feedback contextual da pesquisa
        """
        suggestions = []

        # Sugestões baseadas na qualidade do processamento
        quality = processing_result.get("processing_quality", "fair")

        if quality == "poor":
            suggestions.append(
                "💡 Considere ser mais específico nas suas preferências de marca e modelo"
            )

        # Sugestões baseadas em issues específicos
        for issue in processing_result.get("validation_issues", []):
            if issue["type"] == "low_confidence_brand":
                if issue.get("suggestions"):
                    sugestoes_str = ", ".join(issue["suggestions"][:3])
                    suggestions.append(f"💡 Talvez você quis dizer: {sugestoes_str}?")

            elif issue["type"] == "low_confidence_model":
                suggestions.append(
                    "💡 Verifique a grafia do modelo ou tente um modelo similar"
                )

            elif issue["type"] == "conflicting_preferences":
                suggestions.append(
                    "⚠️ Evite repetir a mesma marca entre principal e alternativas"
                )

        # Sugestões para melhorar o matching
        if not processing_result.get("marcas_alternativas"):
            suggestions.append(
                "💡 Adicionar marcas alternativas pode ampliar suas opções"
            )

        return suggestions


# Instância global do processador
enhanced_brand_processor = EnhancedBrandProcessor()
