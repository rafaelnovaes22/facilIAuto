"""
Validador de Veículos para Transporte de Passageiros (Uber, 99, etc)
Valida se um carro atende aos requisitos das plataformas de transporte
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class AppTransportValidator:
    """
    Validador para veículos de transporte de passageiros
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.app_vehicles_data = None
        self.load_app_vehicles_data()
    
    def load_app_vehicles_data(self):
        """Carregar dados de veículos aceitos para transporte de app"""
        file_path = os.path.join(self.data_dir, "app_transport_vehicles.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.app_vehicles_data = json.load(f)
                print(f"[OK] Dados de transporte de app carregados")
        else:
            print(f"[AVISO] Arquivo {file_path} não encontrado")
            self.app_vehicles_data = None
    
    def is_valid_for_app_transport(
        self, 
        marca: str, 
        modelo: str, 
        ano: int,
        categoria_desejada: str = "uberx_99pop"
    ) -> tuple[bool, Optional[str]]:
        """
        Verificar se um carro é válido para transporte de app
        
        Args:
            marca: Marca do carro
            modelo: Modelo do carro
            ano: Ano de fabricação
            categoria_desejada: uberx_99pop, uber_comfort, uber_black
        
        Returns:
            (is_valid, reason) - Se é válido e motivo se não for
        """
        if not self.app_vehicles_data:
            return True, None  # Se não tem dados, não bloqueia
        
        # Normalizar categoria
        categoria_map = {
            "uberx": "uberx_99pop",
            "99pop": "uberx_99pop",
            "comfort": "uber_comfort",
            "black": "uber_black"
        }
        categoria = categoria_map.get(categoria_desejada.lower(), categoria_desejada)
        
        # Obter dados da categoria
        categorias = self.app_vehicles_data.get("categorias", {})
        categoria_data = categorias.get(categoria)
        
        if not categoria_data:
            return True, None  # Categoria não encontrada, não bloqueia
        
        # 1. Verificar ano mínimo
        ano_minimo = categoria_data.get("ano_minimo_fabricacao", 2015)
        if ano < ano_minimo:
            return False, f"Ano {ano} abaixo do mínimo ({ano_minimo}) para {categoria}"
        
        # 2. Verificar idade máxima
        idade_maxima = categoria_data.get("idade_maxima_anos", 10)
        ano_atual = datetime.now().year
        idade = ano_atual - ano
        if idade > idade_maxima:
            return False, f"Carro muito antigo ({idade} anos, máximo {idade_maxima})"
        
        # 3. Verificar se modelo está na lista de aceitos
        modelos_aceitos = categoria_data.get("modelos_aceitos", [])
        if modelos_aceitos:
            # Normalizar nome do modelo para comparação
            modelo_normalizado = self._normalize_model_name(modelo)
            modelos_normalizados = [self._normalize_model_name(m) for m in modelos_aceitos]
            
            if modelo_normalizado not in modelos_normalizados:
                return False, f"Modelo {modelo} não aceito para {categoria}"
        
        # 4. Verificar se modelo está na lista de excluídos (para algumas categorias)
        modelos_excluidos = categoria_data.get("modelos_excluidos_2025", [])
        if modelos_excluidos:
            modelo_normalizado = self._normalize_model_name(modelo)
            modelos_excluidos_norm = [self._normalize_model_name(m) for m in modelos_excluidos]
            
            if modelo_normalizado in modelos_excluidos_norm:
                return False, f"Modelo {modelo} excluído para {categoria} em 2025"
        
        return True, None
    
    def _normalize_model_name(self, modelo: str) -> str:
        """
        Normalizar nome do modelo para comparação
        Remove espaços extras, converte para minúsculas, remove acentos
        """
        import unicodedata
        
        # Remover acentos
        modelo = ''.join(
            c for c in unicodedata.normalize('NFD', modelo)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Converter para minúsculas e remover espaços extras
        modelo = ' '.join(modelo.lower().split())
        
        # Remover palavras comuns que variam
        palavras_remover = ['sedan', 'hatch', 'hatchback', 'plus', 'lt', 'ltz', 'lx']
        palavras = modelo.split()
        palavras_filtradas = [p for p in palavras if p not in palavras_remover]
        
        return ' '.join(palavras_filtradas)
    
    def get_accepted_categories(
        self,
        marca: str,
        modelo: str,
        ano: int
    ) -> List[Dict[str, any]]:
        """
        Obter todas as categorias de transporte que o carro atende
        
        Args:
            marca: Marca do carro
            modelo: Modelo do carro
            ano: Ano de fabricação
        
        Returns:
            Lista de dicts com categorias aceitas:
            [
                {
                    "categoria": "uberx_99pop",
                    "nome_exibicao": "UberX / 99Pop",
                    "score": 0.9,
                    "descricao": "Categoria econômica"
                },
                ...
            ]
        """
        if not self.app_vehicles_data:
            return []
        
        categorias_aceitas = []
        categorias = self.app_vehicles_data.get("categorias", {})
        
        # Mapeamento de nomes para exibição
        nomes_exibicao = {
            "uberx_99pop": "UberX / 99Pop",
            "uber_comfort": "Uber Comfort",
            "uber_black": "Uber Black"
        }
        
        descricoes = {
            "uberx_99pop": "Categoria econômica - Carros compactos e sedãs",
            "uber_comfort": "Categoria intermediária - Carros mais espaçosos e confortáveis",
            "uber_black": "Categoria premium - Carros de luxo"
        }
        
        # Verificar cada categoria
        for categoria_id, categoria_data in categorias.items():
            is_valid, reason = self.is_valid_for_app_transport(marca, modelo, ano, categoria_id)
            
            if is_valid:
                # Calcular score baseado na idade do carro
                ano_atual = datetime.now().year
                idade = ano_atual - ano
                
                if idade <= 2:
                    score = 1.0
                elif idade <= 5:
                    score = 0.9
                elif idade <= 7:
                    score = 0.7
                else:
                    score = 0.5
                
                categorias_aceitas.append({
                    "categoria": categoria_id,
                    "nome_exibicao": nomes_exibicao.get(categoria_id, categoria_id),
                    "score": score,
                    "descricao": descricoes.get(categoria_id, ""),
                    "ano_minimo": categoria_data.get("ano_minimo_fabricacao", 2015),
                    "idade_maxima": categoria_data.get("idade_maxima_anos", 10)
                })
        
        # Ordenar por score (melhor primeiro)
        categorias_aceitas.sort(key=lambda x: x["score"], reverse=True)
        
        return categorias_aceitas
    
    def get_score_for_app_transport(
        self,
        marca: str,
        modelo: str,
        ano: int,
        categoria_desejada: str = "uberx_99pop"
    ) -> float:
        """
        Obter score de adequação para transporte de app (0.0 a 1.0)
        
        Returns:
            1.0 se totalmente adequado
            0.0 se não atende requisitos
        """
        is_valid, reason = self.is_valid_for_app_transport(marca, modelo, ano, categoria_desejada)
        
        if not is_valid:
            return 0.0
        
        # Se é válido, dar score baseado em quão recente é o carro
        ano_atual = datetime.now().year
        idade = ano_atual - ano
        
        # Carros mais novos têm score maior
        if idade <= 2:
            return 1.0  # Muito novo
        elif idade <= 5:
            return 0.9  # Novo
        elif idade <= 7:
            return 0.7  # Bom
        else:
            return 0.5  # Aceitável mas antigo
    
    def get_recommended_models_for_budget(
        self,
        categoria: str,
        orcamento_min: float,
        orcamento_max: float
    ) -> List[Dict]:
        """
        Obter modelos recomendados para uma categoria e faixa de orçamento
        """
        if not self.app_vehicles_data:
            return []
        
        perfil = self.app_vehicles_data.get("perfis", {}).get("transporte_passageiros", {})
        modelos_por_categoria = perfil.get("top_modelos_por_categoria", {})
        modelos = modelos_por_categoria.get(categoria, [])
        
        # Filtrar por orçamento
        modelos_filtrados = [
            m for m in modelos
            if orcamento_min <= m.get("preco", 0) <= orcamento_max
        ]
        
        return modelos_filtrados


# Singleton para uso global
validator = AppTransportValidator()
