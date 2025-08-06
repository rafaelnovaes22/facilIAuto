"""
Sistema de fallback de imagens para o FacilIAuto
Fornece imagens de alta qualidade quando as originais não funcionam
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple


class VehicleCategory(Enum):
    """Categorias de veículos para fallback"""

    HATCH = "hatch"
    SEDAN = "sedan"
    SUV_COMPACTO = "suv_compacto"
    SUV_MEDIO = "suv_medio"
    SUV_PREMIUM = "suv_premium"
    PICKUP = "pickup"
    CROSSOVER = "crossover"
    ESPORTIVO = "esportivo"
    UTILITARIO = "utilitario"
    MOTO = "moto"


class FallbackImageService:
    """Serviço para gerenciar imagens de fallback"""

    def __init__(self):
        # Configurar logging
        self.logger = logging.getLogger(__name__)

        # Cache para fallbacks já gerados
        self.fallback_cache = {}
        self.cache_expiry = {}
        self.cache_duration = timedelta(hours=24)  # Cache por 24 horas

        # Estatísticas de uso
        self.usage_stats = {
            "fallback_requests": 0,
            "cache_hits": 0,
            "category_usage": {},
            "brand_usage": {},
        }
        # URLs de imagens de fallback de alta qualidade por categoria
        self.fallback_images = {
            VehicleCategory.HATCH: [
                # Hatches modernos e compactos - Alta resolução
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.SEDAN: [
                # Sedans elegantes e executivos - Alta resolução
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.SUV_COMPACTO: [
                # SUVs compactos urbanos - Alta resolução
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.SUV_MEDIO: [
                # SUVs médios familiares - Alta resolução
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.SUV_PREMIUM: [
                # SUVs premium e luxuosos - Alta resolução
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.PICKUP: [
                # Picapes robustas e utilitárias - Alta resolução
                "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.CROSSOVER: [
                # Crossovers versáteis - Alta resolução
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.ESPORTIVO: [
                # Carros esportivos - Alta resolução
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
            VehicleCategory.UTILITARIO: [
                # Veículos utilitários - Alta resolução
                "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85",
            ],
        }

        # Mapeamento de marcas para cores de placeholder
        self.brand_colors = {
            "TOYOTA": "#CC0000",
            "HONDA": "#E60012",
            "VOLKSWAGEN": "#1E3A8A",
            "HYUNDAI": "#002C5F",
            "CHEVROLET": "#FCC200",
            "FORD": "#003478",
            "NISSAN": "#C3002F",
            "BMW": "#0066B2",
            "FIAT": "#8B0000",
            "JEEP": "#1B4332",
            "RENAULT": "#FFCC00",
            "KIA": "#05141F",
            "MITSUBISHI": "#E60012",
            "PEUGEOT": "#0066CC",
            "CAOA": "#FF6600",
        }

        # URLs de placeholder dinâmico
        self.placeholder_services = [
            "https://picsum.photos/400/300?random=",
            "https://source.unsplash.com/400x300/?car,automotive&sig=",
            "https://loremflickr.com/400/300/car,automotive/",
        ]

    def get_fallback_images(
        self, marca: str, modelo: str, categoria: str = None
    ) -> List[str]:
        """
        Obtém imagens de fallback para um veículo específico

        Args:
            marca: Marca do veículo
            modelo: Modelo do veículo
            categoria: Categoria do veículo (opcional)

        Returns:
            Lista de URLs de imagens de fallback
        """
        # Atualizar estatísticas
        self.usage_stats["fallback_requests"] += 1
        if categoria:
            self.usage_stats["category_usage"][categoria] = (
                self.usage_stats["category_usage"].get(categoria, 0) + 1
            )
        if marca:
            self.usage_stats["brand_usage"][marca.upper()] = (
                self.usage_stats["brand_usage"].get(marca.upper(), 0) + 1
            )

        # Verificar cache primeiro
        cache_key = f"{marca.lower()}-{modelo.lower()}-{categoria or 'none'}"
        if self._is_cache_valid(cache_key):
            self.usage_stats["cache_hits"] += 1
            self.logger.debug(f"Cache hit para {cache_key}")
            return self.fallback_cache[cache_key]

        fallback_urls = []

        # 1. Tentar imagens específicas por categoria
        if categoria:
            category_enum = self._get_category_enum(categoria)
            if category_enum and category_enum in self.fallback_images:
                fallback_urls.extend(self.fallback_images[category_enum])

        # 2. Adicionar placeholders dinâmicos personalizados
        vehicle_id = self._generate_vehicle_id(marca, modelo)

        # Placeholder com informações do veículo
        brand_color = self.brand_colors.get(marca.upper(), "#666666")
        text_color = "FFFFFF" if self._is_dark_color(brand_color) else "000000"

        # Placeholder personalizado
        custom_placeholder = f"https://via.placeholder.com/400x300/{brand_color.replace('#', '')}/{text_color}?text={marca}+{modelo}"
        fallback_urls.append(custom_placeholder)

        # 3. Adicionar imagens aleatórias de carros
        for i, service in enumerate(self.placeholder_services):
            if "random=" in service or "sig=" in service:
                fallback_urls.append(f"{service}{int(vehicle_id) + i}")
            else:
                fallback_urls.append(service)

        # 4. Fallback final genérico
        fallback_urls.append(
            "https://via.placeholder.com/400x300/CCCCCC/666666?text=Imagem+Indisponivel"
        )

        result = fallback_urls[
            :5
        ]  # Retornar as 5 melhores opções para maior flexibilidade

        # Armazenar no cache
        self._cache_result(cache_key, result)

        self.logger.info(
            f"Geradas {len(result)} imagens de fallback para {marca} {modelo} ({categoria})"
        )
        return result

    def get_category_fallback_images(self, categoria: str) -> List[str]:
        """
        Obtém imagens de fallback baseadas apenas na categoria

        Args:
            categoria: Categoria do veículo

        Returns:
            Lista de URLs de fallback por categoria
        """
        category_enum = self._get_category_enum(categoria)
        if category_enum and category_enum in self.fallback_images:
            return self.fallback_images[category_enum].copy()

        # Fallback genérico se categoria não encontrada
        return [
            "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=400&h=300&fit=crop&crop=center",
            "https://via.placeholder.com/400x300/666666/FFFFFF?text=Veiculo",
            "https://picsum.photos/400/300?random=1",
        ]

    def get_brand_fallback_images(self, marca: str) -> List[str]:
        """
        Obtém imagens de fallback baseadas na marca

        Args:
            marca: Marca do veículo

        Returns:
            Lista de URLs de fallback por marca
        """
        brand_color = self.brand_colors.get(marca.upper(), "#666666")
        text_color = "FFFFFF" if self._is_dark_color(brand_color) else "000000"

        return [
            f"https://via.placeholder.com/400x300/{brand_color.replace('#', '')}/{text_color}?text={marca}",
            f"https://source.unsplash.com/400x300/?{marca.lower()},car&sig={self._generate_vehicle_id(marca, '')}",
            "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=400&h=300&fit=crop&crop=center",
        ]

    def select_best_fallback(
        self,
        marca: str,
        modelo: str,
        categoria: str = None,
        failed_urls: List[str] = None,
    ) -> str:
        """
        Seleciona a melhor imagem de fallback evitando URLs que já falharam

        Args:
            marca: Marca do veículo
            modelo: Modelo do veículo
            categoria: Categoria do veículo
            failed_urls: URLs que já falharam (para evitar)

        Returns:
            URL da melhor imagem de fallback
        """
        failed_urls = failed_urls or []
        fallback_options = self.get_fallback_images(marca, modelo, categoria)

        # Filtrar URLs que já falharam
        available_options = [url for url in fallback_options if url not in failed_urls]

        if available_options:
            return available_options[0]

        # Se todas as opções falharam, retornar fallback final
        return "https://via.placeholder.com/400x300/CCCCCC/666666?text=Sem+Imagem"

    def get_placeholder_with_info(
        self,
        marca: str,
        modelo: str,
        ano: int = None,
        cor: str = None,
        width: int = 1200,
        height: int = 800,
    ) -> str:
        """
        Gera placeholder personalizado com informações do veículo

        Args:
            marca: Marca do veículo
            modelo: Modelo do veículo
            ano: Ano do veículo (opcional)
            cor: Cor do veículo (opcional)
            width: Largura da imagem
            height: Altura da imagem

        Returns:
            URL do placeholder personalizado
        """
        # Determinar cor de fundo
        if cor and cor.upper() in ["BRANCO", "WHITE"]:
            bg_color = "F8F9FA"
            text_color = "333333"
        elif cor and cor.upper() in ["PRETO", "BLACK"]:
            bg_color = "212529"
            text_color = "FFFFFF"
        else:
            brand_color = self.brand_colors.get(marca.upper(), "#666666")
            bg_color = brand_color.replace("#", "")
            text_color = "FFFFFF" if self._is_dark_color(brand_color) else "000000"

        # Construir texto
        text_parts = [marca.upper(), modelo.upper()]
        if ano:
            text_parts.append(str(ano))

        text = "+".join(text_parts)

        return f"https://via.placeholder.com/{width}x{height}/{bg_color}/{text_color}?text={text}&font_size=24"

    def _get_category_enum(self, categoria: str) -> Optional[VehicleCategory]:
        """Converte string de categoria para enum"""
        category_mapping = {
            "hatch": VehicleCategory.HATCH,
            "sedan": VehicleCategory.SEDAN,
            "suv_compacto": VehicleCategory.SUV_COMPACTO,
            "suv_medio": VehicleCategory.SUV_MEDIO,
            "suv_premium": VehicleCategory.SUV_PREMIUM,
            "pickup": VehicleCategory.PICKUP,
            "crossover": VehicleCategory.CROSSOVER,
            "esportivo": VehicleCategory.ESPORTIVO,
            "utilitario": VehicleCategory.UTILITARIO,
            "moto": VehicleCategory.MOTO,
        }
        return category_mapping.get(categoria.lower())

    def _generate_vehicle_id(self, marca: str, modelo: str) -> str:
        """Gera ID único para o veículo baseado em marca e modelo"""
        combined = f"{marca.lower()}{modelo.lower()}"
        return str(abs(hash(combined)) % 10000)

    def _is_dark_color(self, hex_color: str) -> bool:
        """Determina se uma cor é escura (para escolher cor do texto)"""
        hex_color = hex_color.replace("#", "")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Calcular luminância
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache é válido para uma chave"""
        if cache_key not in self.fallback_cache:
            return False

        if cache_key not in self.cache_expiry:
            return False

        return datetime.now() < self.cache_expiry[cache_key]

    def _cache_result(self, cache_key: str, result: List[str]) -> None:
        """Armazena resultado no cache"""
        self.fallback_cache[cache_key] = result
        self.cache_expiry[cache_key] = datetime.now() + self.cache_duration

    def clear_cache(self) -> None:
        """Limpa o cache de fallbacks"""
        self.fallback_cache.clear()
        self.cache_expiry.clear()
        self.logger.info("Cache de fallback limpo")

    def get_usage_stats(self) -> Dict:
        """Retorna estatísticas de uso do sistema de fallback"""
        total_requests = self.usage_stats["fallback_requests"]
        cache_hits = self.usage_stats["cache_hits"]
        cache_hit_rate = (
            (cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "total_requests": total_requests,
            "cache_hits": cache_hits,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "category_usage": self.usage_stats["category_usage"],
            "brand_usage": self.usage_stats["brand_usage"],
            "cache_size": len(self.fallback_cache),
        }


# Instância global do serviço
fallback_service = FallbackImageService()


# Funções utilitárias para uso fácil
def get_fallback_images(marca: str, modelo: str, categoria: str = None) -> List[str]:
    """Função utilitária para obter imagens de fallback"""
    return fallback_service.get_fallback_images(marca, modelo, categoria)


def get_best_fallback(
    marca: str, modelo: str, categoria: str = None, failed_urls: List[str] = None
) -> str:
    """Função utilitária para obter a melhor imagem de fallback"""
    return fallback_service.select_best_fallback(marca, modelo, categoria, failed_urls)


def create_vehicle_placeholder(
    marca: str, modelo: str, ano: int = None, cor: str = None
) -> str:
    """Função utilitária para criar placeholder personalizado"""
    return fallback_service.get_placeholder_with_info(marca, modelo, ano, cor)
