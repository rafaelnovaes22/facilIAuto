"""
Sistema Avançado de Coleta e Matching de Preferências de Marca/Modelo
Implementa fuzzy matching, auto-complete e validação inteligente
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BrandMatch:
    """Resultado de um match de marca/modelo"""

    original: str
    matched: str
    confidence: float
    suggestions: List[str]


class AdvancedBrandMatcher:
    """Matcher avançado para marcas e modelos com fuzzy matching"""

    def __init__(self):
        # Base de dados expandida de marcas reconhecidas
        self.recognized_brands = {
            "TOYOTA": ["toyota", "toyotta", "toiota", "toyata"],
            "HONDA": ["honda", "handa", "onda"],
            "VOLKSWAGEN": ["volkswagen", "vw", "volks", "folksvagem", "volkswagem"],
            "HYUNDAI": ["hyundai", "hundai", "hiunday", "hyundae"],
            "CHEVROLET": ["chevrolet", "chevy", "chevrolete", "chevrollet"],
            "FORD": ["ford", "forde"],
            "NISSAN": ["nissan", "nisan", "nissam"],
            "BMW": ["bmw", "b.m.w", "beeme"],
            "FIAT": ["fiat", "phiat"],
            "JEEP": ["jeep", "jipe"],
            "RENAULT": ["renault", "reno", "renaut"],
            "KIA": ["kia", "ki-a"],
            "MITSUBISHI": ["mitsubishi", "mitsu", "mitsubichi"],
            "PEUGEOT": ["peugeot", "pegeot", "peujeot"],
            "CAOA": ["caoa", "caoa chery"],
            "AUDI": ["audi", "aud"],
            "MERCEDES": ["mercedes", "mercedes-benz", "mb"],
        }

        # Base de modelos populares por marca
        self.popular_models = {
            "TOYOTA": ["corolla", "hilux", "camry", "prius", "etios", "yaris"],
            "HONDA": ["civic", "city", "fit", "hr-v", "accord", "crv"],
            "VOLKSWAGEN": ["gol", "polo", "jetta", "passat", "tiguan", "fox"],
            "HYUNDAI": ["hb20", "creta", "tucson", "elantra", "ix35"],
            "CHEVROLET": ["onix", "cruze", "tracker", "s10", "cobalt"],
            "FORD": ["ka", "fiesta", "focus", "fusion", "ranger"],
            "NISSAN": ["march", "versa", "sentra", "kicks", "frontier"],
            "BMW": ["320i", "x1", "x3", "318i", "serie 1"],
            "FIAT": ["uno", "argo", "toro", "strada", "palio"],
            "JEEP": ["compass", "renegade", "commander", "wrangler"],
        }

        self.confidence_threshold = 0.6  # Limite mínimo para considerar um match

    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        if not text:
            return ""
        return re.sub(r"[^a-zA-Z0-9]", "", text.lower().strip())

    def calculate_similarity(self, a: str, b: str) -> float:
        """Calcula similaridade entre duas strings"""
        return SequenceMatcher(
            None, self.normalize_text(a), self.normalize_text(b)
        ).ratio()

    def find_best_brand_match(self, user_input: str) -> BrandMatch:
        """Encontra a melhor correspondência para uma marca"""
        normalized_input = self.normalize_text(user_input)

        if not normalized_input:
            return BrandMatch(user_input, "sem_preferencia", 0.0, [])

        best_match = ""
        best_confidence = 0.0
        suggestions = []

        # Busca em marcas reconhecidas e variações
        for brand, variations in self.recognized_brands.items():
            # Testa a marca principal
            similarity = self.calculate_similarity(normalized_input, brand.lower())
            if similarity > best_confidence:
                best_confidence = similarity
                best_match = brand

            # Testa variações
            for variation in variations:
                similarity = self.calculate_similarity(normalized_input, variation)
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = brand

        # Gera sugestões se a confiança não for alta
        if best_confidence < 0.9:
            suggestions = self._generate_brand_suggestions(user_input)

        return BrandMatch(
            original=user_input,
            matched=best_match
            if best_confidence >= self.confidence_threshold
            else user_input,
            confidence=best_confidence,
            suggestions=suggestions[:3],  # Top 3 sugestões
        )

    def find_best_model_match(self, user_input: str, brand: str = "") -> BrandMatch:
        """Encontra a melhor correspondência para um modelo"""
        normalized_input = self.normalize_text(user_input)

        if not normalized_input or user_input.lower() in [
            "aberto_opcoes",
            "sem_preferencia",
        ]:
            return BrandMatch(user_input, "aberto_opcoes", 0.0, [])

        best_match = ""
        best_confidence = 0.0
        suggestions = []

        # Se temos uma marca específica, busca apenas nela
        models_to_search = []
        if brand and brand.upper() in self.popular_models:
            models_to_search = self.popular_models[brand.upper()]
        else:
            # Busca em todos os modelos
            for brand_models in self.popular_models.values():
                models_to_search.extend(brand_models)

        # Encontra melhor match
        for model in models_to_search:
            similarity = self.calculate_similarity(normalized_input, model)
            if similarity > best_confidence:
                best_confidence = similarity
                best_match = model

        # Gera sugestões se necessário
        if best_confidence < 0.9:
            suggestions = self._generate_model_suggestions(user_input, brand)

        return BrandMatch(
            original=user_input,
            matched=best_match
            if best_confidence >= self.confidence_threshold
            else user_input,
            confidence=best_confidence,
            suggestions=suggestions[:3],
        )

    def _generate_brand_suggestions(self, user_input: str) -> List[str]:
        """Gera sugestões de marcas baseadas na entrada"""
        suggestions = []
        normalized_input = self.normalize_text(user_input)

        for brand, variations in self.recognized_brands.items():
            # Verifica se começa com as mesmas letras
            if brand.lower().startswith(normalized_input[:2]):
                suggestions.append(brand)

            # Verifica variações
            for variation in variations:
                if variation.startswith(normalized_input[:2]):
                    suggestions.append(brand)
                    break

        return list(set(suggestions))  # Remove duplicatas

    def _generate_model_suggestions(
        self, user_input: str, brand: str = ""
    ) -> List[str]:
        """Gera sugestões de modelos baseadas na entrada e marca"""
        suggestions = []
        normalized_input = self.normalize_text(user_input)

        models_to_search = []
        if brand and brand.upper() in self.popular_models:
            models_to_search = self.popular_models[brand.upper()]
        else:
            for brand_models in self.popular_models.values():
                models_to_search.extend(brand_models)

        for model in models_to_search:
            if model.lower().startswith(normalized_input[:2]):
                suggestions.append(model.title())

        return suggestions[:5]  # Top 5 sugestões

    def get_autocomplete_suggestions(
        self, query: str, suggestion_type: str = "brand"
    ) -> List[str]:
        """Retorna sugestões para auto-complete"""
        if len(query) < 2:
            return []

        if suggestion_type == "brand":
            return self._generate_brand_suggestions(query)
        elif suggestion_type == "model":
            return self._generate_model_suggestions(query)

        return []

    def validate_and_normalize_preferences(
        self, marca: str, modelo: str
    ) -> Dict[str, Any]:
        """Valida e normaliza preferências de marca e modelo"""
        brand_match = self.find_best_brand_match(marca)
        model_match = self.find_best_model_match(modelo, brand_match.matched)

        return {
            "marca_original": marca,
            "marca_normalizada": brand_match.matched,
            "marca_confianca": brand_match.confidence,
            "marca_sugestoes": brand_match.suggestions,
            "modelo_original": modelo,
            "modelo_normalizado": model_match.matched,
            "modelo_confianca": model_match.confidence,
            "modelo_sugestoes": model_match.suggestions,
            "needs_confirmation": (
                brand_match.confidence < 0.8
                or model_match.confidence < 0.8
                or len(brand_match.suggestions) > 0
            ),
        }


# Instância global do matcher
brand_matcher = AdvancedBrandMatcher()
