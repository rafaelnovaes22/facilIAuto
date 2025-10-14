"""
Sistema de Classificação Inteligente de Carros
Classifica veículos por categoria baseado no nome/modelo e infere características típicas
"""

from typing import Dict, List, Tuple
import re


class CarClassifier:
    """
    Classificador inteligente de carros por categoria
    """
    
    # Mapeamento de padrões de modelo → categoria
    MODEL_PATTERNS = {
        'SUV': [
            'tracker', 'creta', 'kicks', 't-cross', 'tcross', 'tiggo', 
            'compass', 'renegade', 'hr-v', 'hrv', 'wrv', 'ecosport', 'duster',
            'captur', 'tucson', 'sportage', 'seltos', 'stonic', 'xc',
            'edge', 'equinox', 'trailblazer', 'blazer', 'outlander',
            'cx-5', 'cx-3', 'rav4', 'crv', 'cr-v', 'asx', 'vitara'
        ],
        'Sedan': [
            'hb20s', 'cronos', 'logan', 'corolla', 'civic', 'city',
            'prisma', 'voyage', 'virtus', 'jetta', 'polo sedan', 'arrizo',
            'versa', 'sentra', 'cruze sedan', 'focus sedan', 'fusion',
            'accord', 'camry', 'passat', 'variant', 'spacefox'
        ],
        'Pickup': [
            'frontier', 'strada', 'saveiro', 'montana', 'toro',
            'hilux', 'ranger', 's10', 'amarok', 'l200', 'triton',
            'navara', 'ram', 'silverado', 'colorado', 'gladiator'
        ],
        'Hatch': [
            'onix', 'gol', 'fox', 'up', 'fit', 'march', 
            'sandero', 'hb20', 'polo', 'punto', 'palio',
            'uno', 'ka', '208', '207', 'clio', 'fluence',
            'fiesta', 'focus hatch', 'golf', 'i30', 'cerato',
            'yaris', 'etios', 'corsa', 'celta', 'agile'
        ],
        'Compacto': [
            'kwid', 'mobi', 'picanto', 'spark', 'etios hatch',
            'up!', 'fox bluemotion', 'gol city', 'celta',
            'atos', 'i10', 'march', 'smart', 'mini'
        ],
        'Van': [
            'doblo', 'kangoo', 'partner', 'spin', 'zafira',
            'caravan', 'grand caravan', 'voyager', 'sienna',
            'odyssey', 'quest', 'sorento', 'carnival',
            'minivan', 'multivan', 'caravelle', 'sharan', 'touran',
            'espace', 'scenic', 'c4 picasso', 'grand picasso'
        ]
    }
    
    # Itens típicos de segurança por ano
    SAFETY_BY_YEAR = {
        2024: ['ABS', 'airbag', 'controle_estabilidade', '6_airbags', 'ISOFIX', 'camera_re'],
        2022: ['ABS', 'airbag', 'controle_estabilidade', '6_airbags', 'ISOFIX'],
        2020: ['ABS', 'airbag', 'controle_estabilidade', 'airbag_lateral'],
        2018: ['ABS', 'airbag', 'controle_estabilidade'],
        2015: ['ABS', 'airbag'],
        2010: ['ABS'],
    }
    
    # Itens típicos de conforto por categoria
    COMFORT_BY_CATEGORY = {
        'SUV': ['ar_condicionado', 'direcao_eletrica', 'vidro_eletrico', 'trava_eletrica', 
                'sensor_estacionamento', 'computador_bordo'],
        'Sedan': ['ar_condicionado', 'direcao_eletrica', 'vidro_eletrico', 'trava_eletrica',
                  'computador_bordo'],
        'Pickup': ['ar_condicionado', 'direcao_eletrica', 'vidro_eletrico', 'trava_eletrica'],
        'Van': ['ar_condicionado', 'direcao_eletrica', 'vidro_eletrico', 'trava_eletrica',
                'sensor_estacionamento'],
        'Hatch': ['ar_condicionado', 'direcao_eletrica', 'vidro_eletrico'],
        'Compacto': ['ar_condicionado', 'direcao_eletrica'],
    }
    
    # Versões premium que justificam itens extras
    PREMIUM_KEYWORDS = [
        'premier', 'limited', 'platinum', 'exclusive', 'top', 'highline',
        'prestige', 'luxury', 'titanium', 'ultimate', 'elite', 'ltz',
        'xlt', 'xls', 's.design', 'r-design', 'sport', 'gtline'
    ]
    
    def classify(self, nome: str, modelo: str) -> str:
        """
        Classificar categoria baseado no nome/modelo
        
        Args:
            nome: Nome do carro (ex: "CHEVROLET TRACKER T")
            modelo: Modelo do carro (ex: "CHEVROLET TRACKER T")
        
        Returns:
            Categoria: SUV, Sedan, Pickup, Hatch, Compacto, Van
        """
        # Normalizar para lowercase para comparação
        search_text = f"{nome} {modelo}".lower()
        
        # Buscar padrões em ordem de especificidade
        # 1. Pickup (mais específico)
        for pattern in self.MODEL_PATTERNS['Pickup']:
            if pattern in search_text:
                return 'Pickup'
        
        # 2. Van (específico)
        for pattern in self.MODEL_PATTERNS['Van']:
            if pattern in search_text:
                return 'Van'
        
        # 3. SUV (pode confundir com Hatch)
        for pattern in self.MODEL_PATTERNS['SUV']:
            if pattern in search_text:
                return 'SUV'
        
        # 4. Sedan (detectar "s" no final ou palavra sedan)
        for pattern in self.MODEL_PATTERNS['Sedan']:
            if pattern in search_text:
                return 'Sedan'
        
        # 5. Compacto (subconjunto de Hatch)
        for pattern in self.MODEL_PATTERNS['Compacto']:
            if pattern in search_text:
                return 'Compacto'
        
        # 6. Hatch (padrão se não for nada acima)
        for pattern in self.MODEL_PATTERNS['Hatch']:
            if pattern in search_text:
                return 'Hatch'
        
        # Default: Hatch (maioria dos carros populares)
        return 'Hatch'
    
    def get_typical_safety_items(self, ano: int, categoria: str, modelo: str = '') -> List[str]:
        """
        Retornar itens típicos de segurança baseado em ano e categoria
        
        Args:
            ano: Ano do carro
            categoria: Categoria (SUV, Sedan, etc)
            modelo: Modelo do carro (para detectar versões premium)
        
        Returns:
            Lista de itens de segurança
        """
        items = []
        
        # Determinar itens por ano
        if ano >= 2024:
            items = self.SAFETY_BY_YEAR[2024].copy()
        elif ano >= 2022:
            items = self.SAFETY_BY_YEAR[2022].copy()
        elif ano >= 2020:
            items = self.SAFETY_BY_YEAR[2020].copy()
        elif ano >= 2018:
            items = self.SAFETY_BY_YEAR[2018].copy()
        elif ano >= 2015:
            items = self.SAFETY_BY_YEAR[2015].copy()
        elif ano >= 2010:
            items = self.SAFETY_BY_YEAR[2010].copy()
        else:
            items = []
        
        # SUVs geralmente têm mais segurança
        if categoria == 'SUV' and ano >= 2018:
            if 'camera_re' not in items:
                items.append('camera_re')
            if 'sensor_estacionamento' not in items:
                items.append('sensor_estacionamento')
        
        # Detectar versões premium
        modelo_lower = modelo.lower()
        is_premium = any(keyword in modelo_lower for keyword in self.PREMIUM_KEYWORDS)
        
        if is_premium and ano >= 2018:
            if '6_airbags' not in items:
                items.append('6_airbags')
            if 'ISOFIX' not in items and ano >= 2016:
                items.append('ISOFIX')
            if 'camera_re' not in items:
                items.append('camera_re')
        
        return items
    
    def get_typical_comfort_items(self, categoria: str, ano: int, modelo: str = '') -> List[str]:
        """
        Retornar itens típicos de conforto baseado em categoria e ano
        
        Args:
            categoria: Categoria (SUV, Sedan, etc)
            ano: Ano do carro
            modelo: Modelo do carro (para detectar versões premium)
        
        Returns:
            Lista de itens de conforto
        """
        # Itens base por categoria
        items = self.COMFORT_BY_CATEGORY.get(categoria, ['ar_condicionado']).copy()
        
        # Carros mais novos têm mais conforto
        if ano >= 2020:
            if 'retrovisor_eletrico' not in items:
                items.append('retrovisor_eletrico')
            if 'ar_condicionado_digital' not in items and categoria in ['SUV', 'Sedan']:
                items.append('ar_condicionado_digital')
        
        # Detectar versões premium
        modelo_lower = modelo.lower()
        is_premium = any(keyword in modelo_lower for keyword in self.PREMIUM_KEYWORDS)
        
        if is_premium:
            if 'banco_couro' not in items:
                items.append('banco_couro')
            if 'central_multimidia' not in items:
                items.append('central_multimidia')
            if 'sensor_estacionamento' not in items:
                items.append('sensor_estacionamento')
        
        return items
    
    def get_typical_features(self, marca: str, modelo: str, categoria: str, ano: int) -> Dict[str, List[str]]:
        """
        Retornar conjunto completo de características típicas
        
        Args:
            marca: Marca do carro
            modelo: Modelo do carro
            categoria: Categoria (SUV, Sedan, etc)
            ano: Ano do carro
        
        Returns:
            Dict com itens_seguranca e itens_conforto
        """
        return {
            'itens_seguranca': self.get_typical_safety_items(ano, categoria, modelo),
            'itens_conforto': self.get_typical_comfort_items(categoria, ano, modelo)
        }
    
    def is_premium_version(self, modelo: str) -> bool:
        """Detectar se é versão premium"""
        modelo_lower = modelo.lower()
        return any(keyword in modelo_lower for keyword in self.PREMIUM_KEYWORDS)


# Singleton para uso global
classifier = CarClassifier()

