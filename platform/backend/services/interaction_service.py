"""
🤖 ML System: Serviço de Coleta e Gerenciamento de Interações

Responsável por persistir e recuperar dados de interações dos usuários
para treinamento de modelos de Machine Learning.

Autor: AI Engineer
Data: Outubro 2024
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from models.interaction import InteractionEvent, InteractionStats, InteractionType


class InteractionService:
    """
    Serviço para gerenciar interações dos usuários com veículos.
    
    Responsabilidades:
    - Salvar eventos de interação em arquivo JSON
    - Recuperar interações para treinamento de ML
    - Calcular estatísticas de uso
    - Garantir integridade dos dados
    """
    
    def __init__(self, data_dir: str = "data/interactions"):
        """
        Inicializa o serviço de interações.
        
        Args:
            data_dir: Diretório onde os dados serão armazenados
        """
        self.data_dir = Path(data_dir)
        self.interactions_file = self.data_dir / "user_interactions.json"
        
        # Criar diretório se não existir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar arquivo se não existir
        if not self.interactions_file.exists():
            self._initialize_file()
    
    def _initialize_file(self):
        """Inicializa arquivo de interações com estrutura vazia"""
        initial_data = {
            "interactions": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_count": 0,
                "version": "1.0"
            }
        }
        
        with open(self.interactions_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Arquivo de interações inicializado: {self.interactions_file}")
    
    def save_interaction(self, event: InteractionEvent) -> bool:
        """
        Salva um evento de interação no arquivo JSON.
        
        Args:
            event: Evento de interação a ser salvo
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            # Carregar dados existentes
            with open(self.interactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converter evento para dict
            event_dict = event.dict()
            
            # Converter datetime para string ISO
            if isinstance(event_dict.get('timestamp'), datetime):
                event_dict['timestamp'] = event_dict['timestamp'].isoformat()
            
            # Adicionar ID único
            event_dict['id'] = f"int_{len(data['interactions']) + 1:06d}"
            
            # Adicionar à lista
            data['interactions'].append(event_dict)
            
            # Atualizar metadata
            data['metadata']['last_updated'] = datetime.now().isoformat()
            data['metadata']['total_count'] = len(data['interactions'])
            
            # Salvar de volta
            with open(self.interactions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Interação salva: {event.interaction_type} - Car: {event.car_id}")
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao salvar interação: {e}")
            return False
    
    def get_all_interactions(self) -> List[Dict]:
        """
        Retorna todas as interações armazenadas.
        
        Returns:
            Lista de dicionários com todas as interações
        """
        try:
            with open(self.interactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('interactions', [])
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar interações: {e}")
            return []
    
    def get_interactions_count(self) -> int:
        """
        Retorna o total de interações coletadas.
        
        Returns:
            Número total de interações
        """
        try:
            with open(self.interactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('metadata', {}).get('total_count', 0)
            
        except Exception as e:
            print(f"[ERRO] Falha ao contar interações: {e}")
            return 0
    
    def get_stats(self) -> InteractionStats:
        """
        Calcula e retorna estatísticas agregadas das interações.
        
        Returns:
            Objeto InteractionStats com estatísticas calculadas
        """
        try:
            interactions = self.get_all_interactions()
            
            if not interactions:
                return InteractionStats()
            
            # Contadores
            click_count = 0
            view_details_count = 0
            whatsapp_contact_count = 0
            unique_sessions = set()
            unique_cars = set()
            durations = []
            last_interaction = None
            
            for interaction in interactions:
                # Contar por tipo
                interaction_type = interaction.get('interaction_type')
                if interaction_type == InteractionType.CLICK:
                    click_count += 1
                elif interaction_type == InteractionType.VIEW_DETAILS:
                    view_details_count += 1
                elif interaction_type == InteractionType.WHATSAPP_CONTACT:
                    whatsapp_contact_count += 1
                
                # Coletar IDs únicos
                unique_sessions.add(interaction.get('session_id'))
                unique_cars.add(interaction.get('car_id'))
                
                # Coletar durações
                duration = interaction.get('duration_seconds')
                if duration is not None:
                    durations.append(duration)
                
                # Última interação
                timestamp_str = interaction.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if last_interaction is None or timestamp > last_interaction:
                            last_interaction = timestamp
                    except:
                        pass
            
            # Calcular média de duração
            avg_duration = sum(durations) / len(durations) if durations else None
            
            return InteractionStats(
                total_interactions=len(interactions),
                click_count=click_count,
                view_details_count=view_details_count,
                whatsapp_contact_count=whatsapp_contact_count,
                unique_sessions=len(unique_sessions),
                unique_cars=len(unique_cars),
                avg_duration_seconds=avg_duration,
                last_interaction=last_interaction
            )
            
        except Exception as e:
            print(f"[ERRO] Falha ao calcular estatísticas: {e}")
            return InteractionStats()
    
    def get_interactions_by_session(self, session_id: str) -> List[Dict]:
        """
        Retorna todas as interações de uma sessão específica.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de interações da sessão
        """
        interactions = self.get_all_interactions()
        return [i for i in interactions if i.get('session_id') == session_id]
    
    def get_interactions_by_car(self, car_id: str) -> List[Dict]:
        """
        Retorna todas as interações com um carro específico.
        
        Args:
            car_id: ID do carro
            
        Returns:
            Lista de interações com o carro
        """
        interactions = self.get_all_interactions()
        return [i for i in interactions if i.get('car_id') == car_id]
    
    def get_interactions_for_training(self, min_count: int = 500) -> Optional[List[Dict]]:
        """
        Retorna interações se houver dados suficientes para treinamento.
        
        Args:
            min_count: Número mínimo de interações necessárias
            
        Returns:
            Lista de interações se houver dados suficientes, None caso contrário
        """
        interactions = self.get_all_interactions()
        
        if len(interactions) >= min_count:
            print(f"[OK] {len(interactions)} interações disponíveis para treinamento")
            return interactions
        else:
            print(f"[INFO] Apenas {len(interactions)} interações. Mínimo necessário: {min_count}")
            return None
