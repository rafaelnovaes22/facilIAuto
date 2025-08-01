"""
Módulo para acesso aos dados do PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
from app.config import DATABASE_CONFIG

class CarroRepository:
    """Repository para acessar dados de carros do PostgreSQL"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
    
    def _get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def get_all_carros(self) -> List[Dict]:
        """Obtém todos os carros disponíveis"""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT 
                    id,
                    marca,
                    modelo,
                    versao,
                    ano,
                    combustivel,
                    cambio,
                    cor,
                    km,
                    preco,
                    preco_promocional,
                    fotos,
                    descricao,
                    opcionais,
                    disponivel,
                    destaque,
                    concessionaria_id
                FROM veiculos 
                WHERE disponivel = true
                ORDER BY destaque DESC, preco ASC
            """
            
            cursor.execute(query)
            veiculos_db = cursor.fetchall()
            
            # Converte para formato compatível com o sistema existente
            carros = []
            for veiculo in veiculos_db:
                carro = self._converter_veiculo_para_formato_sistema(veiculo)
                carros.append(carro)
            
            return carros
            
        finally:
            cursor.close()
            conn.close()
    
    def get_carro_by_id(self, carro_id: str) -> Optional[Dict]:
        """Obtém um carro específico por ID"""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT 
                    id,
                    marca,
                    modelo,
                    versao,
                    ano,
                    combustivel,
                    cambio,
                    cor,
                    km,
                    preco,
                    preco_promocional,
                    fotos,
                    descricao,
                    opcionais,
                    disponivel,
                    destaque,
                    concessionaria_id
                FROM veiculos 
                WHERE id = %s AND disponivel = true
            """
            
            cursor.execute(query, (carro_id,))
            veiculo = cursor.fetchone()
            
            if veiculo:
                return self._converter_veiculo_para_formato_sistema(veiculo)
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def buscar_carros_por_filtros(self, filtros: Dict) -> List[Dict]:
        """Busca carros com filtros específicos"""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Constrói query dinâmica baseada nos filtros
            where_clauses = ["disponivel = true"]
            params = []
            
            if filtros.get("marca"):
                where_clauses.append("UPPER(marca) = UPPER(%s)")
                params.append(filtros["marca"])
            
            if filtros.get("modelo"):
                where_clauses.append("UPPER(modelo) LIKE UPPER(%s)")
                params.append(f"%{filtros['modelo']}%")
            
            if filtros.get("ano_min"):
                where_clauses.append("ano >= %s")
                params.append(filtros["ano_min"])
            
            if filtros.get("ano_max"):
                where_clauses.append("ano <= %s")
                params.append(filtros["ano_max"])
            
            if filtros.get("preco_min"):
                where_clauses.append("preco >= %s")
                params.append(filtros["preco_min"])
            
            if filtros.get("preco_max"):
                where_clauses.append("preco <= %s")
                params.append(filtros["preco_max"])
            
            if filtros.get("combustivel"):
                where_clauses.append("UPPER(combustivel) = UPPER(%s)")
                params.append(filtros["combustivel"])
            
            query = f"""
                SELECT 
                    id,
                    marca,
                    modelo,
                    versao,
                    ano,
                    combustivel,
                    cambio,
                    cor,
                    km,
                    preco,
                    preco_promocional,
                    fotos,
                    descricao,
                    opcionais,
                    disponivel,
                    destaque,
                    concessionaria_id
                FROM veiculos 
                WHERE {' AND '.join(where_clauses)}
                ORDER BY destaque DESC, preco ASC
            """
            
            cursor.execute(query, params)
            veiculos_db = cursor.fetchall()
            
            # Converte para formato compatível
            carros = []
            for veiculo in veiculos_db:
                carro = self._converter_veiculo_para_formato_sistema(veiculo)
                carros.append(carro)
            
            return carros
            
        finally:
            cursor.close()
            conn.close()
    
    def _converter_veiculo_para_formato_sistema(self, veiculo: Dict) -> Dict:
        """Converte veículo do banco para formato usado pelo sistema de recomendação"""
        
        # Mapeia combustível
        combustivel_map = {
            "FLEX": "flex",
            "GASOLINA": "gasolina", 
            "ETANOL": "etanol",
            "DIESEL": "diesel",
            "ELETRICO": "eletrico",
            "HIBRIDO": "hibrido"
        }
        
        # Mapeia câmbio
        cambio_map = {
            "MANUAL": "manual",
            "AUTOMATICO": "automatico",
            "AUTOMATIZADO": "automatizado",
            "CVT": "cvt"
        }
        
        # Determina categoria baseada no modelo
        categoria = self._determinar_categoria(veiculo["modelo"], veiculo.get("versao", ""))
        
        # Estima atributos baseados nos dados disponíveis
        atributos = self._estimar_atributos(veiculo)
        
        # Determina uso recomendado
        uso_recomendado = self._determinar_uso_recomendado(categoria, veiculo)
        
        # Determina disponibilidade (simula baseado no destaque)
        disponibilidade = "imediata" if veiculo.get("destaque") else "30_dias"
        
        return {
            "id": veiculo["id"],
            "marca": veiculo["marca"],
            "modelo": veiculo["modelo"],
            "versao": veiculo.get("versao"),
            "ano": veiculo["ano"],
            "preco": float(veiculo["preco"]),
            "preco_promocional": float(veiculo["preco_promocional"]) if veiculo.get("preco_promocional") else None,
            "categoria": categoria,
            "consumo": atributos["consumo"],  # Estimado
            "potencia": atributos["potencia"],  # Estimado
            "capacidade_pessoas": atributos["capacidade_pessoas"],  # Estimado
            "porta_malas": atributos["porta_malas"],  # Estimado
            "combustivel": combustivel_map.get(veiculo["combustivel"], "flex"),
            "cambio": cambio_map.get(veiculo.get("cambio", "MANUAL"), "manual"),
            "cor": veiculo.get("cor"),
            "km": veiculo.get("km", 0),
            "uso_recomendado": uso_recomendado,
            "familia": atributos["familia"],
            "seguranca": atributos["seguranca"],  # Estimado
            "conforto": atributos["conforto"],  # Estimado
            "economia": atributos["economia"],  # Estimado
            "performance": atributos["performance"],  # Estimado
            "disponibilidade": disponibilidade,
            "regiao": ["SP", "RJ", "MG", "PR", "SC", "RS"],  # Default - pode ser expandido
            "fotos": veiculo.get("fotos", []),
            "descricao": veiculo.get("descricao"),
            "opcionais": veiculo.get("opcionais", []),
            "destaque": veiculo.get("destaque", False)
        }
    
    def _determinar_categoria(self, modelo: str, versao: str = "") -> str:
        """Determina a categoria do veículo baseado no modelo"""
        modelo_lower = modelo.lower()
        versao_lower = versao.lower() if versao else ""
        
        # SUVs e Crossovers
        if any(word in modelo_lower for word in ["tucson", "compass", "kicks", "t-cross", "nivus", "creta", "hr-v", "tracker"]):
            return "suv_compacto"
        
        if any(word in modelo_lower for word in ["santa fe", "sorento", "pilot", "pathfinder"]):
            return "suv_medio"
        
        if any(word in modelo_lower for word in ["x1", "x3", "q3", "glc", "macan"]):
            return "suv_premium"
        
        # Picapes
        if any(word in modelo_lower for word in ["ranger", "hilux", "amarok", "frontier", "s10", "toro"]):
            return "pickup"
        
        # Sedans
        if any(word in modelo_lower for word in ["corolla", "civic", "jetta", "cruze", "sentra", "city"]):
            return "sedan"
        
        # Hatches
        if any(word in modelo_lower for word in ["onix", "hb20", "polo", "gol", "argo", "ka", "march"]):
            return "hatch"
        
        # Default baseado na versão ou tamanho típico
        if "sedan" in versao_lower or "plus" in modelo_lower:
            return "sedan"
        
        return "hatch"  # Default
    
    def _estimar_atributos(self, veiculo: Dict) -> Dict:
        """Estima atributos baseado no modelo e características conhecidas"""
        modelo = veiculo["modelo"].lower()
        categoria = self._determinar_categoria(veiculo["modelo"])
        ano = veiculo["ano"]
        
        # Estimativas baseadas em dados típicos do mercado
        if categoria == "hatch":
            return {
                "consumo": 13.0,
                "potencia": 110,
                "capacidade_pessoas": 5,
                "porta_malas": 300,
                "familia": "pequeno",
                "seguranca": 4,
                "conforto": 3,
                "economia": 5,
                "performance": 3
            }
        elif categoria == "sedan":
            return {
                "consumo": 12.0,
                "potencia": 150,
                "capacidade_pessoas": 5,
                "porta_malas": 500,
                "familia": "medio",
                "seguranca": 5,
                "conforto": 4,
                "economia": 4,
                "performance": 4
            }
        elif categoria in ["suv_compacto", "suv_medio"]:
            return {
                "consumo": 10.5,
                "potencia": 170,
                "capacidade_pessoas": 5,
                "porta_malas": 450,
                "familia": "medio",
                "seguranca": 5,
                "conforto": 4,
                "economia": 3,
                "performance": 4
            }
        elif categoria == "pickup":
            return {
                "consumo": 8.5,
                "potencia": 200,
                "capacidade_pessoas": 4,
                "porta_malas": 1000,
                "familia": "utilitario",
                "seguranca": 5,
                "conforto": 4,
                "economia": 2,
                "performance": 5
            }
        else:
            # Default
            return {
                "consumo": 11.0,
                "potencia": 130,
                "capacidade_pessoas": 5,
                "porta_malas": 400,
                "familia": "medio",
                "seguranca": 4,
                "conforto": 4,
                "economia": 4,
                "performance": 3
            }
    
    def _determinar_uso_recomendado(self, categoria: str, veiculo: Dict) -> List[str]:
        """Determina uso recomendado baseado na categoria"""
        uso_map = {
            "hatch": ["urbano", "primeiro_carro"],
            "sedan": ["urbano", "viagem", "familia"],
            "suv_compacto": ["urbano", "familia"],
            "suv_medio": ["urbano", "viagem", "familia"],
            "suv_premium": ["urbano", "viagem", "luxo"],
            "pickup": ["trabalho", "aventura", "carga"]
        }
        
        return uso_map.get(categoria, ["urbano"])

# Instância global do repository
carro_repo = CarroRepository()

# Funções de compatibilidade com o sistema existente
def get_carros() -> List[Dict]:
    """Função compatível que retorna carros do PostgreSQL"""
    return carro_repo.get_all_carros()

def get_carro_by_id(carro_id: str) -> Optional[Dict]:
    """Função compatível que retorna carro por ID do PostgreSQL"""
    return carro_repo.get_carro_by_id(carro_id) 