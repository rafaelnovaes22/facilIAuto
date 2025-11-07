"""
Serviço para obter preço atualizado de combustível
Busca de múltiplas fontes com fallback
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path


class FuelPriceService:
    """
    Serviço para obter preço atualizado de GASOLINA
    
    Fontes (em ordem de prioridade):
    1. Variável de ambiente FUEL_PRICE
    2. Cache local (válido por 7 dias)
    3. API externa (se configurada)
    4. Valor padrão (R$ 6,17 - gasolina)
    
    Nota: Sempre usa preço da GASOLINA para cálculos de TCO,
    independente do tipo de combustível do veículo (Flex, Etanol, etc)
    """
    
    # Preço padrão de GASOLINA (atualizado manualmente quando necessário)
    # Fonte: ANP - Agência Nacional do Petróleo
    DEFAULT_PRICE = 6.17  # R$ 6,17/L gasolina (março 2025)
    
    # Duração do cache (7 dias)
    CACHE_DURATION_DAYS = 7
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / "fuel_price_cache.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_price(self, state: str = "SP") -> float:
        """
        Obtém preço atual da GASOLINA
        
        Args:
            state: Estado para buscar preço regional (futuro)
            
        Returns:
            Preço da gasolina em R$/L
        """
        # 1. Tentar variável de ambiente (para deploy fácil)
        env_price = os.getenv("FUEL_PRICE")
        if env_price:
            try:
                price = float(env_price)
                if 3.0 <= price <= 10.0:  # Validação de sanidade
                    print(f"[FUEL] Usando preço da variável de ambiente: R$ {price:.2f}/L")
                    return price
            except ValueError:
                pass
        
        # 2. Tentar cache local
        cached_price = self._get_cached_price()
        if cached_price:
            print(f"[FUEL] Usando preço do cache: R$ {cached_price:.2f}/L")
            return cached_price
        
        # 3. Tentar buscar de API externa
        api_price = self._fetch_from_api(state)
        if api_price:
            self._save_to_cache(api_price)
            print(f"[FUEL] Preço obtido da API: R$ {api_price:.2f}/L")
            return api_price
        
        # 4. Fallback para preço padrão
        print(f"[FUEL] Usando preço padrão: R$ {self.DEFAULT_PRICE:.2f}/L")
        return self.DEFAULT_PRICE
    
    def _get_cached_price(self) -> Optional[float]:
        """
        Obtém preço do cache se ainda válido
        
        Returns:
            Preço em cache ou None se expirado/inexistente
        """
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Verificar se cache ainda é válido
            cached_date = datetime.fromisoformat(cache_data['timestamp'])
            age_days = (datetime.now() - cached_date).days
            
            if age_days <= self.CACHE_DURATION_DAYS:
                return cache_data['price']
            else:
                print(f"[FUEL] Cache expirado ({age_days} dias)")
                return None
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[FUEL] Erro ao ler cache: {e}")
            return None
    
    def _save_to_cache(self, price: float):
        """
        Salva preço no cache
        
        Args:
            price: Preço a ser salvo
        """
        try:
            cache_data = {
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'source': 'api'
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"[FUEL] Preço salvo no cache: R$ {price:.2f}/L")
        
        except Exception as e:
            print(f"[FUEL] Erro ao salvar cache: {e}")
    
    def _fetch_from_api(self, state: str) -> Optional[float]:
        """
        Busca preço de API externa
        
        Args:
            state: Estado para buscar preço
            
        Returns:
            Preço obtido ou None se falhar
            
        Nota: Implementação futura - pode usar API da ANP ou similar
        """
        # TODO: Implementar integração com API da ANP ou similar
        # Por enquanto, retorna None para usar fallback
        
        # Exemplo de implementação futura:
        # try:
        #     response = requests.get(
        #         f"https://api.anp.gov.br/precos/gasolina/{state}",
        #         timeout=5
        #     )
        #     if response.status_code == 200:
        #         data = response.json()
        #         return data.get('preco_medio')
        # except Exception as e:
        #     print(f"[FUEL] Erro ao buscar da API: {e}")
        
        return None
    
    def update_default_price(self, new_price: float):
        """
        Atualiza preço padrão e salva no cache
        
        Args:
            new_price: Novo preço padrão
        """
        if 3.0 <= new_price <= 10.0:
            self._save_to_cache(new_price)
            print(f"[FUEL] Preço padrão atualizado: R$ {new_price:.2f}/L")
        else:
            raise ValueError(f"Preço inválido: R$ {new_price:.2f}/L")
    
    def get_price_info(self) -> Dict:
        """
        Obtém informações sobre o preço atual
        
        Returns:
            Dicionário com preço e metadados
        """
        price = self.get_current_price()
        
        # Verificar fonte
        source = "default"
        if os.getenv("FUEL_PRICE"):
            source = "environment"
        elif self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    cached_date = datetime.fromisoformat(cache_data['timestamp'])
                    age_days = (datetime.now() - cached_date).days
                    if age_days <= self.CACHE_DURATION_DAYS:
                        source = "cache"
            except:
                pass
        
        return {
            "price": price,
            "source": source,
            "last_updated": datetime.now().isoformat(),
            "default_price": self.DEFAULT_PRICE
        }


# Instância global do serviço
fuel_price_service = FuelPriceService()
