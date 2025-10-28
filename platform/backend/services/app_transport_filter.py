"""
Filtro e validação de carros para transporte por aplicativo (Uber, 99)
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from models.car import Car


class AppTransportFilter:
    """
    Filtro especializado para carros de transporte por aplicativo
    
    Valida se um carro atende aos requisitos de:
    - UberX / 99Pop
    - Uber Comfort
    - Uber Black
    """
    
    def __init__(self, data_dir: str = None):
        """
        Inicializar filtro com dados de veículos aceitos
        
        Args:
            data_dir: Diretório com arquivo app_transport_vehicles.json
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "data"
            )
        
        # Carregar dados de veículos aceitos
        vehicles_file = os.path.join(data_dir, "app_transport_vehicles.json")
        with open(vehicles_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.requisitos_gerais = self.data['requisitos_gerais']
        self.categorias = self.data['categorias']
        self.eletricos_hibridos = self.data['eletricos_hibridos']
        
        # Criar índice de modelos por categoria
        self._build_model_index()
    
    def _build_model_index(self):
        """Construir índice de modelos aceitos por categoria"""
        self.model_index = {}
        
        for categoria_id, categoria_data in self.categorias.items():
            for modelo in categoria_data['modelos_aceitos']:
                # Normalizar nome do modelo
                modelo_norm = self._normalize_model_name(modelo)
                
                if modelo_norm not in self.model_index:
                    self.model_index[modelo_norm] = []
                
                self.model_index[modelo_norm].append(categoria_id)
    
    def _normalize_model_name(self, nome: str) -> str:
        """
        Normalizar nome do modelo para comparação
        
        Args:
            nome: Nome do modelo
            
        Returns:
            Nome normalizado (lowercase, sem acentos, sem espaços extras)
        """
        import unicodedata
        
        # Remover acentos
        nome = unicodedata.normalize('NFKD', nome)
        nome = nome.encode('ASCII', 'ignore').decode('ASCII')
        
        # Lowercase e remover espaços extras
        nome = nome.lower().strip()
        nome = ' '.join(nome.split())
        
        return nome
    
    def is_accepted_for_app(
        self, 
        car: Car, 
        categoria: str = "uberx_99pop"
    ) -> bool:
        """
        Verificar se carro é aceito para transporte por app
        
        Args:
            car: Instância do modelo Car
            categoria: "uberx_99pop", "uber_comfort" ou "uber_black"
            
        Returns:
            True se aceito, False caso contrário
        """
        # Validar requisitos gerais
        if not self._check_requisitos_gerais(car):
            return False
        
        # Validar categoria específica
        if categoria not in self.categorias:
            return False
        
        categoria_data = self.categorias[categoria]
        
        # Validar ano de fabricação
        ano_atual = datetime.now().year
        idade_maxima = categoria_data['idade_maxima_anos']
        ano_minimo = ano_atual - idade_maxima
        
        if car.ano < ano_minimo:
            return False
        
        # Validar modelo
        car_model_norm = self._normalize_model_name(f"{car.marca} {car.modelo}")
        
        # Verificar se modelo está na lista aceita
        for modelo_aceito in categoria_data['modelos_aceitos']:
            modelo_norm = self._normalize_model_name(modelo_aceito)
            
            # Match exato ou parcial (ex: "Onix" match "Onix Plus")
            if modelo_norm in car_model_norm or car_model_norm in modelo_norm:
                return True
        
        return False
    
    def _check_requisitos_gerais(self, car: Car) -> bool:
        """
        Verificar requisitos gerais (4 portas, 5 lugares, ar-condicionado)
        
        Args:
            car: Instância do modelo Car
            
        Returns:
            True se atende requisitos, False caso contrário
        """
        # Verificar portas (se disponível)
        if hasattr(car, 'portas') and car.portas is not None:
            if car.portas < self.requisitos_gerais['portas_minimo']:
                return False
        
        # Verificar lugares (assumir 5 se não especificado)
        lugares = getattr(car, 'lugares', 5)
        if lugares < self.requisitos_gerais['lugares_minimo']:
            return False
        
        # Verificar ar-condicionado (assumir True se não especificado)
        ar_condicionado = getattr(car, 'ar_condicionado', True)
        if not ar_condicionado:
            return False
        
        return True
    
    def get_accepted_categories(self, car: Car) -> List[str]:
        """
        Obter todas as categorias para as quais o carro é aceito
        
        Args:
            car: Instância do modelo Car
            
        Returns:
            Lista de categorias aceitas
        """
        categorias_aceitas = []
        
        for categoria_id in self.categorias.keys():
            if self.is_accepted_for_app(car, categoria_id):
                categorias_aceitas.append(categoria_id)
        
        return categorias_aceitas
    
    def filter_cars_for_app(
        self, 
        cars: List[Car], 
        categoria: str = "uberx_99pop"
    ) -> List[Car]:
        """
        Filtrar lista de carros para transporte por app
        
        Args:
            cars: Lista de carros
            categoria: Categoria desejada
            
        Returns:
            Lista de carros aceitos
        """
        return [
            car for car in cars 
            if self.is_accepted_for_app(car, categoria)
        ]
    
    def get_categoria_info(self, categoria: str) -> Optional[Dict]:
        """
        Obter informações sobre uma categoria
        
        Args:
            categoria: ID da categoria
            
        Returns:
            Dicionário com informações da categoria
        """
        return self.categorias.get(categoria)
    
    def get_recommended_priorities(self, categoria: str) -> Dict[str, int]:
        """
        Obter prioridades recomendadas para uma categoria
        
        Args:
            categoria: ID da categoria
            
        Returns:
            Dicionário com prioridades (1-5)
        """
        if categoria not in self.categorias:
            return {}
        
        return self.categorias[categoria].get('prioridades_recomendadas', {})
    
    def is_electric_or_hybrid(self, car: Car) -> bool:
        """
        Verificar se carro é elétrico ou híbrido
        
        Args:
            car: Instância do modelo Car
            
        Returns:
            True se elétrico/híbrido, False caso contrário
        """
        # Verificar por combustível
        if hasattr(car, 'combustivel'):
            combustivel_lower = car.combustivel.lower()
            if any(termo in combustivel_lower for termo in ['eletrico', 'hibrido', 'hybrid', 'electric', 'phev']):
                return True
        
        # Verificar por modelo
        car_model = f"{car.marca} {car.modelo}".lower()
        
        for item in self.eletricos_hibridos['modelos']:
            marca_lower = item['marca'].lower()
            if marca_lower in car_model:
                for modelo in item['modelos']:
                    if modelo.lower() in car_model:
                        return True
        
        return False
    
    def get_operational_cost(self, categoria: str) -> Optional[Dict]:
        """
        Obter custo operacional estimado para uma categoria
        
        Args:
            categoria: ID da categoria
            
        Returns:
            Dicionário com custos mensais estimados
        """
        custos = self.data.get('custo_operacional_mensal', {})
        return custos.get(categoria)
    
    def get_recommendations_by_profile(self, perfil: str) -> Optional[Dict]:
        """
        Obter recomendações por perfil de motorista
        
        Args:
            perfil: "iniciante", "intermediario", "profissional", "sustentavel"
            
        Returns:
            Dicionário com recomendações
        """
        recomendacoes = self.data.get('recomendacoes_por_perfil', {})
        return recomendacoes.get(perfil)
    
    def enrich_car_with_app_info(self, car: Car) -> Dict:
        """
        Enriquecer informações do carro com dados de transporte por app
        
        Args:
            car: Instância do modelo Car
            
        Returns:
            Dicionário com informações enriquecidas
        """
        categorias_aceitas = self.get_accepted_categories(car)
        is_eletrico = self.is_electric_or_hybrid(car)
        
        info = {
            "aceito_para_app": len(categorias_aceitas) > 0,
            "categorias_aceitas": categorias_aceitas,
            "categorias_nomes": [
                self.categorias[cat]['nome'] 
                for cat in categorias_aceitas
            ],
            "is_eletrico_hibrido": is_eletrico,
            "requisitos_atendidos": {
                "portas": getattr(car, 'portas', 4) >= 4,
                "lugares": getattr(car, 'lugares', 5) >= 5,
                "ar_condicionado": getattr(car, 'ar_condicionado', True)
            }
        }
        
        # Adicionar custo operacional da melhor categoria
        if categorias_aceitas:
            melhor_categoria = categorias_aceitas[-1]  # Última = melhor
            custo = self.get_operational_cost(melhor_categoria)
            if custo:
                info['custo_operacional_mensal'] = custo
        
        return info


# Exemplo de uso
if __name__ == "__main__":
    # Teste básico
    filter = AppTransportFilter()
    
    # Criar carro de teste
    from models.car import Car
    
    test_car = Car(
        id="test_001",
        nome="CHEVROLET ONIX PLUS 1.0",
        marca="Chevrolet",
        modelo="Onix Plus",
        ano=2022,
        preco=75000,
        quilometragem=30000,
        categoria="Sedan",
        combustivel="Flex",
        portas=4,
        dealership_id="test",
        dealership_name="Test Dealer",
        dealership_city="São Paulo",
        dealership_state="SP"
    )
    
    # Testar filtros
    print("=== Teste de Filtro de Transporte por App ===\n")
    
    print(f"Carro: {test_car.nome}")
    print(f"Ano: {test_car.ano}")
    print(f"Marca: {test_car.marca}")
    print(f"Modelo: {test_car.modelo}\n")
    
    # Verificar categorias
    for categoria in ['uberx_99pop', 'uber_comfort', 'uber_black']:
        aceito = filter.is_accepted_for_app(test_car, categoria)
        categoria_nome = filter.categorias[categoria]['nome']
        print(f"{categoria_nome}: {'✅ Aceito' if aceito else '❌ Não aceito'}")
    
    print("\n" + "="*50 + "\n")
    
    # Informações enriquecidas
    info = filter.enrich_car_with_app_info(test_car)
    print("Informações Enriquecidas:")
    print(f"Aceito para app: {info['aceito_para_app']}")
    print(f"Categorias aceitas: {', '.join(info['categorias_nomes'])}")
    print(f"Elétrico/Híbrido: {info['is_eletrico_hibrido']}")
    
    if 'custo_operacional_mensal' in info:
        custo = info['custo_operacional_mensal']
        print(f"\nCusto Operacional Mensal:")
        print(f"  Total: R$ {custo['total']['min']:,.2f} - R$ {custo['total']['max']:,.2f}")

