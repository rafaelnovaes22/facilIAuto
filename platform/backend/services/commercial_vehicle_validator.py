"""
Validador de Veículos Comerciais
Critérios baseados em uso profissional real (entregas, transporte de carga)

🚚 REGRAS CRÍTICAS:
1. Pickups médias/grandes (Toro, Frontier, L200, Hilux, Ranger, S10) são LAZER/AVENTURA, NÃO comerciais!
2. VUCs e caminhões leves (HR, Bongo, Accelo) são para CARGA PESADA, não entregas leves!

Veículos comerciais para ENTREGAS LEVES/MÉDIAS:
- Pickups pequenas (Strada, Saveiro, Montana)
- Furgões (Fiorino, Kangoo, Ducato, Master, Sprinter)
- Vans (Kombi, Master, Sprinter)

VUCs/Caminhões (uso específico - CARGA PESADA):
- Hyundai HR, Kia Bongo, Mercedes-Benz Accelo
- Requerem CNH categoria C ou superior
- Não são adequados para entregas urbanas leves
"""

from typing import Tuple, Optional


class CommercialVehicleValidator:
    """
    Valida se um veículo é adequado para uso comercial profissional
    """
    
    # Pickups PEQUENAS comerciais (caçamba curta, motor básico)
    COMMERCIAL_PICKUPS = {
        "Fiat": ["Strada"],
        "Volkswagen": ["Saveiro"],
        "Chevrolet": ["Montana"],
        "Renault": ["Oroch"]  # Apenas versões básicas
    }
    
    # Furgões e vans comerciais (CARGA)
    COMMERCIAL_VANS = {
        "Fiat": ["Fiorino", "Ducato", "Doblo Cargo"],
        "Renault": ["Kangoo", "Master"],
        "Citroën": ["Berlingo", "Jumper"],
        "Peugeot": ["Partner", "Boxer"],
        "Mercedes-Benz": ["Sprinter", "Vito"],
        "Volkswagen": ["Kombi", "Transporter"],
        "Iveco": ["Daily"],
        "Ford": ["Transit"]
    }
    
    # Vans de passageiros (PESSOAS - 8+ passageiros)
    # Não são para Uber/99, mas para fretamento, escolar, turismo
    PASSENGER_VANS = {
        "Fiat": ["Ducato Minibus"],
        "Renault": ["Master Minibus"],
        "Mercedes-Benz": ["Sprinter Executiva", "Sprinter Van"],
        "Volkswagen": ["Kombi Lotação"],
        "Iveco": ["Daily Minibus"],
        "Peugeot": ["Boxer Minibus"]
    }
    
    # VUCs e Caminhões Leves (NÃO são para entregas leves - requerem CNH C)
    VUCS_TRUCKS = {
        "Hyundai": ["HR", "HD"],
        "Kia": ["Bongo", "K2500"],
        "Mercedes-Benz": ["Accelo", "Atego"],
        "Volkswagen": ["Delivery"],
        "Ford": ["Cargo"],
        "Iveco": ["Tector"],
        "JAC": ["J6"]
    }
    
    # Pickups MÉDIAS/GRANDES que NÃO são comerciais (são lazer/aventura)
    LEISURE_PICKUPS = {
        "Fiat": ["Toro"],
        "Nissan": ["Frontier"],
        "Mitsubishi": ["L200", "Triton"],
        "Toyota": ["Hilux"],
        "Ford": ["Ranger"],
        "Chevrolet": ["S10"],
        "Volkswagen": ["Amarok"],
        "RAM": ["1500", "2500"]
    }
    
    # Versões que indicam uso comercial (palavras-chave)
    COMMERCIAL_KEYWORDS = [
        "endurance",
        "robust",
        "hard working",
        "cargo",
        "furgão",
        "van",
        "cs",  # Cabine simples
        "working"
    ]
    
    # Versões que indicam uso lazer/aventura (NÃO comercial)
    LEISURE_KEYWORDS = [
        "ranch",
        "volcano",
        "freedom",
        "trailhawk",
        "sport",
        "adventure",
        "4x4",
        "cd",  # Cabine dupla (geralmente lazer)
        "limited",
        "premium",
        "black",
        "ultra"
    ]
    
    def is_commercial_vehicle(
        self,
        marca: str,
        modelo: str,
        versao: Optional[str] = None,
        categoria: Optional[str] = None,
        strict_mode: bool = True
    ) -> Tuple[bool, str]:
        """
        Valida se o veículo é comercial
        
        Args:
            strict_mode: Se True, rejeita veículos inadequados. 
                        Se False, aceita mas retorna aviso.
        
        Returns:
            (is_valid, reason)
        """
        modelo_lower = modelo.lower()
        versao_lower = (versao or "").lower()
        
        # 1. Verificar se é VUC/Caminhão (carga pesada)
        for marca_vuc, modelos_vuc in self.VUCS_TRUCKS.items():
            if marca.lower() == marca_vuc.lower():
                for modelo_vuc in modelos_vuc:
                    if modelo_vuc.lower() in modelo_lower:
                        if strict_mode:
                            return False, f"{marca} {modelo} é VUC/caminhão para carga pesada (requer CNH C), não para entregas leves"
                        else:
                            return True, f"⚠️ VUC/Caminhão - Requer CNH C - Adequado apenas para carga pesada"
        
        # 2. Verificar se é pickup MÉDIA/GRANDE (lazer)
        for marca_leisure, modelos_leisure in self.LEISURE_PICKUPS.items():
            if marca.lower() == marca_leisure.lower():
                for modelo_leisure in modelos_leisure:
                    if modelo_leisure.lower() in modelo_lower:
                        if strict_mode:
                            return False, f"{marca} {modelo} é pickup de lazer/aventura, não comercial"
                        else:
                            return True, f"⚠️ Pickup de lazer - Alto custo operacional - Não recomendado para entregas"
        
        # 3. Verificar se é van de PASSAGEIROS - REJEITAR para uso comercial
        if self.is_passenger_van(marca, modelo, versao):
            if strict_mode:
                return False, f"{marca} {modelo} é van de passageiros (8+ pessoas), não para entregas comerciais"
            else:
                return True, f"⚠️ Van de passageiros - Use perfil 'Transporte de Passageiros'"
        
        # 4. Verificar se é furgão/van COMERCIAL (carga) - ACEITAR
        for marca_van, modelos_van in self.COMMERCIAL_VANS.items():
            if marca.lower() == marca_van.lower():
                for modelo_van in modelos_van:
                    if modelo_van.lower() in modelo_lower:
                        return True, f"Furgão/van comercial (carga)"
        
        # 5. Verificar se é pickup PEQUENA comercial
        for marca_pickup, modelos_pickup in self.COMMERCIAL_PICKUPS.items():
            if marca.lower() == marca_pickup.lower():
                for modelo_pickup in modelos_pickup:
                    if modelo_pickup.lower() in modelo_lower:
                        # Verificar versão para confirmar uso comercial
                        if versao_lower:
                            # Se tem palavra-chave de lazer, REJEITAR
                            if any(keyword in versao_lower for keyword in self.LEISURE_KEYWORDS):
                                return False, f"Versão {versao} é para lazer, não comercial"
                            
                            # Se tem palavra-chave comercial, ACEITAR
                            if any(keyword in versao_lower for keyword in self.COMMERCIAL_KEYWORDS):
                                return True, f"Pickup comercial (versão {versao})"
                        
                        # Sem versão especificada, aceitar pickup pequena
                        return True, f"Pickup comercial"
        
        # 6. Verificar categoria
        if categoria:
            categoria_lower = categoria.lower()
            
            # Rejeitar VUCs e caminhões
            if "vuc" in categoria_lower or "caminhão" in categoria_lower or "caminhao" in categoria_lower:
                return False, "VUC/caminhão para carga pesada (requer CNH C), não para entregas leves"
            
            # Aceitar furgões e vans
            if "furgão" in categoria_lower or "furgao" in categoria_lower or "van" in categoria_lower:
                return True, "Categoria comercial (furgão/van)"
        
        # 7. Não é veículo comercial
        return False, "Não é veículo comercial (use pickups pequenas ou furgões)"
    
    def get_commercial_requirements(self) -> dict:
        """
        Retorna requisitos técnicos para veículos comerciais
        """
        return {
            "capacidade_carga_minima_kg": 500,
            "chassi_reforcado": True,
            "suspensao_reforçada": True,
            "motor_diesel_preferivel": True,
            "consumo_minimo_kml": 9.0,
            "manutencao_acessivel": True,
            "durabilidade_alta": True,
            "conforto_secundario": True,
            "tecnologia_basica": True
        }
    
    def get_commercial_categories(self) -> list:
        """
        Retorna categorias válidas para uso comercial
        """
        return [
            "Pickup Pequena",
            "Furgão",
            "Van",
            "Utilitário"
        ]
    
    def get_leisure_pickups_list(self) -> list:
        """
        Retorna lista de pickups que NÃO são comerciais
        """
        result = []
        for marca, modelos in self.LEISURE_PICKUPS.items():
            for modelo in modelos:
                result.append(f"{marca} {modelo}")
        return result
    
    def get_vucs_trucks_list(self) -> list:
        """
        Retorna lista de VUCs e caminhões (não adequados para entregas leves)
        """
        result = []
        for marca, modelos in self.VUCS_TRUCKS.items():
            for modelo in modelos:
                result.append(f"{marca} {modelo}")
        return result
    
    def is_vuc_or_truck(self, marca: str, modelo: str) -> bool:
        """
        Verifica se é VUC ou caminhão
        """
        modelo_lower = modelo.lower()
        for marca_vuc, modelos_vuc in self.VUCS_TRUCKS.items():
            if marca.lower() == marca_vuc.lower():
                for modelo_vuc in modelos_vuc:
                    if modelo_vuc.lower() in modelo_lower:
                        return True
        return False
    
    def is_passenger_van(self, marca: str, modelo: str, versao: Optional[str] = None) -> bool:
        """
        Verifica se é van de passageiros (8+ pessoas)
        Não confundir com van comercial (carga)
        """
        modelo_lower = modelo.lower()
        versao_lower = (versao or "").lower()
        
        # Palavras-chave que indicam van de passageiros
        passenger_keywords = ["minibus", "executiva", "lotação", "escolar", "passageiros"]
        
        # Verificar palavras-chave na versão
        if versao_lower and any(keyword in versao_lower for keyword in passenger_keywords):
            return True
        
        # Verificar lista de vans de passageiros
        for marca_van, modelos_van in self.PASSENGER_VANS.items():
            if marca.lower() == marca_van.lower():
                for modelo_van in modelos_van:
                    if modelo_van.lower() in modelo_lower:
                        return True
        
        return False
    
    def get_commercial_suitability(
        self,
        marca: str,
        modelo: str,
        versao: Optional[str] = None,
        categoria: Optional[str] = None
    ) -> dict:
        """
        Retorna nível de adequação do veículo para uso comercial
        
        Returns:
            {
                "nivel": "ideal" | "adequado" | "limitado" | "inadequado",
                "score": 0.0-1.0,
                "tipo": "pickup_pequena" | "furgao" | "pickup_lazer" | "vuc",
                "avisos": ["aviso1", "aviso2"],
                "requer_cnh": "B" | "C",
                "recomendado": bool
            }
        """
        modelo_lower = modelo.lower()
        
        # Van de Passageiros (8+ pessoas)
        if self.is_passenger_van(marca, modelo, versao):
            return {
                "nivel": "inadequado",
                "score": 0.0,
                "tipo": "van_passageiros",
                "avisos": [
                    "⚠️ Van de passageiros (8+ pessoas)",
                    "⚠️ Não é para entregas comerciais",
                    "⚠️ Use perfil 'Transporte de Passageiros' (fretamento, escolar, turismo)",
                    "⚠️ Não é aceita em Uber/99 (exceto Uber Van em algumas cidades)"
                ],
                "requer_cnh": "D",
                "recomendado": False
            }
        
        # VUC/Caminhão
        if self.is_vuc_or_truck(marca, modelo):
            return {
                "nivel": "limitado",
                "score": 0.3,
                "tipo": "vuc_caminhao",
                "avisos": [
                    "⚠️ Requer CNH categoria C ou superior",
                    "⚠️ Adequado apenas para carga pesada (1.500kg+)",
                    "⚠️ Alto custo operacional",
                    "⚠️ Manutenção cara"
                ],
                "requer_cnh": "C",
                "recomendado": False
            }
        
        # Pickup de lazer
        for marca_leisure, modelos_leisure in self.LEISURE_PICKUPS.items():
            if marca.lower() == marca_leisure.lower():
                for modelo_leisure in modelos_leisure:
                    if modelo_leisure.lower() in modelo_lower:
                        return {
                            "nivel": "inadequado",
                            "score": 0.2,
                            "tipo": "pickup_lazer",
                            "avisos": [
                                "⚠️ Projetada para lazer/aventura, não entregas",
                                "⚠️ Alto consumo de combustível",
                                "⚠️ Manutenção cara",
                                "⚠️ Custo operacional 70% maior que pickups pequenas"
                            ],
                            "requer_cnh": "B",
                            "recomendado": False
                        }
        
        # Furgão/Van
        for marca_van, modelos_van in self.COMMERCIAL_VANS.items():
            if marca.lower() == marca_van.lower():
                for modelo_van in modelos_van:
                    if modelo_van.lower() in modelo_lower:
                        return {
                            "nivel": "ideal",
                            "score": 1.0,
                            "tipo": "furgao_van",
                            "avisos": [],
                            "requer_cnh": "B",
                            "recomendado": True
                        }
        
        # Pickup pequena
        for marca_pickup, modelos_pickup in self.COMMERCIAL_PICKUPS.items():
            if marca.lower() == marca_pickup.lower():
                for modelo_pickup in modelos_pickup:
                    if modelo_pickup.lower() in modelo_lower:
                        return {
                            "nivel": "ideal",
                            "score": 0.95,
                            "tipo": "pickup_pequena",
                            "avisos": [],
                            "requer_cnh": "B",
                            "recomendado": True
                        }
        
        # Outros (Sedan, SUV, etc)
        return {
            "nivel": "inadequado",
            "score": 0.0,
            "tipo": "outro",
            "avisos": [
                "⚠️ Não é veículo comercial",
                "⚠️ Use pickups pequenas, furgões ou vans"
            ],
            "requer_cnh": "B",
            "recomendado": False
        }


# Instância global
validator = CommercialVehicleValidator()
