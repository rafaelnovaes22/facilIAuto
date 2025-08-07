"""
MVP de Machine Learning integrado com toda infraestrutura existente
Aproveita: Memory Manager, LangGraph, Uso Principal, Busca Inteligente
"""

import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from app.brand_matcher import AdvancedBrandMatcher
from app.busca_inteligente import EstadoBuscaDict, calcular_scores_compatibilidade
from app.enhanced_brand_processor import EnhancedBrandProcessor
from app.memory_manager import ConversationMemoryManager
from app.memory_ml_integration import get_memory_ml_extension
from app.models import CarroRecomendacao, QuestionarioBusca

# Aproveitar TUDO que já temos
from app.uso_principal_processor import UsoMatcher

logger = logging.getLogger(__name__)


class IntegratedMLCollector:
    """
    Coletor que aproveita o Memory Manager existente para ML
    """

    def __init__(self):
        # Reusar o Memory Manager que já temos!
        self.memory = ConversationMemoryManager()
        self.data_path = Path("data/ml_training")
        self.data_path.mkdir(parents=True, exist_ok=True)

    def collect_from_conversation(
        self,
        conversation_id: Optional[str],
        user_session_id: Optional[str],
        carro: Dict[str, Any],
        score: float,
        user_action: Optional[str] = None,
        questionario: Optional[QuestionarioBusca] = None,
        rule_score: Optional[float] = None,
        ml_score: Optional[float] = None,
        ml_confidence: Optional[float] = None,
        method: Optional[str] = None,
    ):
        """
        Coleta dados aproveitando o sistema de memória existente
        """
        # Buscar contexto da conversa no Memory Manager
        if conversation_id:
            conversation, messages = self.memory.get_conversation_history(
                conversation_id
            )
            if not conversation:
                return
            user_session_id = conversation.user_session_id
            carro_id = conversation.carro_id
        else:
            # Se não há conversation_id, usar user_session_id diretamente
            if not user_session_id:
                return
            carro_id = carro.get("id")

        # Extrair preferências do usuário da conversa
        user_context = self.memory.get_user_context(user_session_id, carro_id)

        # Combinar com dados do carro e score
        ml_data = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "user_session_id": user_session_id,
            "carro_features": self._extract_enhanced_features(carro),
            "user_preferences": user_context.get("preferences", {}),
            "conversation_metrics": {
                "message_count": user_context.get("total_messages", 0),
                "agents_used": user_context.get("preferred_agents", {}),
                "session_duration": user_context.get("session_duration", 0),
            },
            "calculated_score": score,
            "user_action": user_action,
            "feedback_score": self._calculate_feedback_score(user_action, user_context),
        }

        # Salvar para treinamento
        self._save_training_data(ml_data)

        # Também persistir no Memory Manager para histórico
        self.memory.persist_ml_feedback(
            conversation_id=conversation_id, ml_data=ml_data
        )

    def _extract_enhanced_features(self, carro: Dict) -> Dict:
        """
        Extrai features aproveitando processadores existentes
        """
        features = {
            # Features básicas
            "preco": carro.get("preco", 0),
            "ano": carro.get("ano", 0),
            "km": carro.get("km", 0),
            "consumo": carro.get("consumo", 0),
            # Usar Brand Matcher para normalizar marca
            "marca_normalizada": AdvancedBrandMatcher().normalize_text(
                carro.get("marca", "")
            ),
            # Número de imagens disponíveis
            "n_imagens": len(carro.get("fotos", [])),
            # Score de uso principal existente
            "uso_urbano_score": self._get_uso_score(carro, "urbano"),
            "uso_viagem_score": self._get_uso_score(carro, "viagem"),
            "uso_trabalho_score": self._get_uso_score(carro, "trabalho"),
            "uso_familia_score": self._get_uso_score(carro, "familia"),
        }

        return features

    def _get_uso_score(self, carro: Dict, uso: str) -> float:
        """
        Aproveita o UsoMatcher existente para features
        """
        try:
            matcher = UsoMatcher()
            # Criar QuestionarioBusca mínimo com valores padrão
            questionario = QuestionarioBusca(
                marca_preferida="sem_preferencia",
                modelo_especifico="aberto_opcoes",
                urgencia="sem_pressa",
                regiao="SP",
                uso_principal=[uso],
                pessoas_transportar=2,
                espaco_carga="medio",
                potencia_desejada="media",
                prioridade="equilibrio",
            )
            score_result = matcher.calcular_score_uso_principal(questionario, carro)
            (
                score_valor,
                _,
                _,
            ) = score_result  # Extrair apenas o score da tupla (score, razões, pontos_fortes)
            return score_valor
        except Exception:
            return 0.0

    def _calculate_feedback_score(
        self, action: Optional[str], user_context: Dict
    ) -> float:
        """
        Calcula score baseado em ação e contexto
        """
        base_scores = {
            "contact": 1.0,
            "schedule": 0.9,
            "like": 0.8,
            "share": 0.7,
            "view_details": 0.6,
            "ask_question": 0.5,
            "view": 0.4,
            "ignore": 0.1,
            None: 0.3,
        }

        score = base_scores.get(action, 0.3)

        # Ajustar baseado no engajamento (mensagens na conversa)
        message_count = user_context.get("total_messages", 0)
        if message_count > 10:
            score *= 1.3
        elif message_count > 5:
            score *= 1.1

        return min(1.0, score)

    def _save_training_data(self, data: Dict):
        """
        Salva dados para treinamento
        """
        file_path = self.data_path / f"ml_data_{datetime.now().strftime('%Y%m')}.jsonl"
        with open(file_path, "a") as f:
            f.write(json.dumps(data) + "\n")


class SmartMVPModel:
    """
    Modelo ML que aproveita toda inteligência já construída
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False

        # Componentes existentes
        self.uso_matcher = UsoMatcher()
        self.brand_processor = EnhancedBrandProcessor()
        self.memory = ConversationMemoryManager()

        # Carregar modelo se existir
        self.model_path = Path("models/smart_mvp_model.pkl")
        self.load_model()

    def prepare_smart_features(
        self,
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
        conversation_id: Optional[str] = None,
    ) -> np.ndarray:
        """
        Prepara features usando toda inteligência existente
        """
        features = []

        # 1. Features do sistema de busca inteligente
        estado_busca: EstadoBuscaDict = {
            "questionario": questionario,
            "carros_disponiveis": [carro],
            "carros_filtrados": [carro],
            "pontuacoes": [],
            "recomendacoes_finais": [],
            "resumo_perfil": "",
            "sugestoes_personalizadas": [],
        }
        resultado_busca = calcular_scores_compatibilidade(estado_busca)
        if resultado_busca.get("pontuacoes"):
            score_data = resultado_busca["pontuacoes"][0]
            features.extend(
                [
                    score_data.get("score", 0),
                    score_data.get("score", 0) * 0.2,  # Aproximação para score_preco
                    score_data.get("score", 0)
                    * 0.15,  # Aproximação para score_categoria
                    score_data.get("score", 0) * 0.1,  # Aproximação para score_economia
                    score_data.get("score", 0)
                    * 0.1,  # Aproximação para score_opcionais
                ]
            )
        else:
            features.extend([0, 0, 0, 0, 0])

        # 2. Features do Uso Principal (aproveitar cálculos complexos)
        (
            uso_score,
            uso_razoes,
            uso_fortes,
        ) = self.uso_matcher.calcular_score_uso_principal(questionario, carro)
        features.append(uso_score)
        features.append(len(uso_razoes))  # Quantidade de razões
        features.append(len(uso_fortes))  # Quantidade de pontos fortes

        # 3. Features do Brand Processor
        brand_validation = self.brand_processor.process_and_validate_preferences(
            {
                "marca_preferida": questionario.marca_preferida,
                "modelo_especifico": questionario.modelo_especifico,
            }
        )
        features.append(1 if brand_validation.get("is_valid") else 0)
        features.append(brand_validation.get("confidence", 0))

        # 4. Features do Memory Manager (se tiver conversa)
        if conversation_id:
            conversation_data = self.memory.get_conversation(conversation_id)
            if conversation_data:
                features.extend(
                    [
                        len(conversation_data.messages),  # Engajamento
                        1
                        if conversation_data.primary_agent
                        else 0,  # Tem agente principal
                        conversation_data.total_interactions or 0,
                    ]
                )
            else:
                features.extend([0, 0, 0])
        else:
            features.extend([0, 0, 0])

        # 5. Features básicas do carro (normalizadas)
        features.extend(
            [
                carro.get("preco", 0) / 100000,
                (2024 - carro.get("ano", 2020)) / 10,
                carro.get("km", 0) / 100000,
                carro.get("consumo", 10) / 20,
                carro.get("cilindrada", 1.0) / 3.0,
                carro.get("porta_malas_litros", 300) / 600,
                carro.get("lugares", 5) / 7,
                carro.get("seguranca", 3) / 5,
            ]
        )

        # 6. Features categóricas
        features.append(1 if carro.get("categoria") == "SUV" else 0)
        features.append(1 if carro.get("categoria") == "Sedan" else 0)
        features.append(1 if carro.get("categoria") == "Hatch" else 0)
        features.append(1 if carro.get("combustivel") == "Flex" else 0)
        features.append(1 if carro.get("cambio") == "Automático" else 0)

        # 7. Features do questionário
        features.append(
            questionario.orcamento_max / 200000 if questionario.orcamento_max else 0.5
        )
        features.append(0)  # primeiro_veiculo não existe mais - usando valor padrão
        features.append(
            questionario.pessoas_transportar / 7
            if questionario.pessoas_transportar
            else 0.5
        )
        features.append(0.5)  # km_mensal não existe mais - usando valor padrão

        # 8. Opcionais importantes (aproveitar análise existente)
        opcionais_text = " ".join(carro.get("opcionais", [])).lower()
        important_features = [
            "ar condicionado",
            "direção",
            "airbag",
            "abs",
            "android auto",
            "apple carplay",
            "sensor",
            "câmera",
            "automático",
            "couro",
            "teto solar",
            "rodas",
        ]
        for feature in important_features:
            features.append(1 if feature in opcionais_text else 0)

        return np.array(features)

    def train_with_smart_data(self, min_samples: int = 30):
        """
        Treina usando dados coletados inteligentemente
        """
        # Buscar dados do Memory Manager e arquivos
        all_data = self._load_all_training_data()

        if len(all_data) < min_samples:
            logger.warning(f"Apenas {len(all_data)} amostras. Mínimo: {min_samples}")
            return False

        # Preparar dados
        X_list: List[Any] = []
        y_list: List[Any] = []
        weights_list: List[float] = []  # Pesos baseados em confiança

        for data in all_data:
            try:
                # Reconstruir questionário
                questionario = QuestionarioBusca(**data.get("user_preferences", {}))

                # Preparar features
                features = self.prepare_smart_features(
                    data["carro_features"], questionario, data.get("conversation_id")
                )

                X_list.append(features)

                # Target: combinação inteligente
                rule_score = data.get("calculated_score", 0.5)
                feedback_score = data.get("feedback_score", 0.5)

                # Peso baseado em engajamento
                weight = 1.0
                if data.get("conversation_metrics", {}).get("message_count", 0) > 5:
                    weight = 1.5  # Mais peso para conversas longas

                # Score final ponderado
                final_score = 0.4 * rule_score + 0.6 * feedback_score

                y_list.append(final_score)
                weights_list.append(weight)

            except Exception as e:
                logger.error(f"Erro ao processar amostra: {e}")
                continue

        if len(X_list) < min_samples:
            return False

        # Converter para arrays
        X = np.array(X_list)
        y = np.array(y_list)
        weights = np.array(weights_list)

        # Normalizar features
        X = self.scaler.fit_transform(X)

        # Treinar Random Forest com sample weights
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        )

        self.model.fit(X, y, sample_weight=weights)
        self.is_trained = True

        # Salvar modelo
        self.save_model()

        # Métricas
        train_score = self.model.score(X, y, sample_weight=weights)
        feature_importance = self.model.feature_importances_

        logger.info(f"✅ Modelo treinado com {len(X)} amostras")
        logger.info(f"📊 R² Score: {train_score:.3f}")
        logger.info(f"🎯 Top features: {self._get_top_features(feature_importance)}")

        return True

    def predict_smart(
        self,
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Predição inteligente com explicações
        """
        if not self.is_trained:
            return {
                "score": 0.0,
                "confidence": 0.0,
                "method": "not_trained",
                "explanation": "Modelo ainda não treinado",
            }

        # Preparar features
        features = self.prepare_smart_features(carro, questionario, conversation_id)
        features = features.reshape(1, -1)
        features = self.scaler.transform(features)

        # Predição
        score = self.model.predict(features)[0]

        # Confidence baseada em árvores
        predictions = [tree.predict(features)[0] for tree in self.model.estimators_]
        std = np.std(predictions)
        confidence = max(0.3, 1 - std)

        # Feature importance para explicação
        feature_imp = self.model.feature_importances_
        top_features_idx = np.argsort(feature_imp)[-5:][::-1]

        # Gerar explicação
        feature_names = self._get_feature_names()
        explanations = []
        for idx in top_features_idx:
            if idx < len(feature_names):
                importance = feature_imp[idx]
                if importance > 0.05:
                    explanations.append(f"{feature_names[idx]}: {importance:.0%}")

        return {
            "score": float(score),
            "confidence": float(confidence),
            "method": "smart_ml",
            "explanations": explanations,
            "tree_agreement": 1 - std,
            "n_trees": len(self.model.estimators_),
        }

    def _load_all_training_data(self) -> List[Dict]:
        """
        Carrega dados de treinamento de múltiplas fontes
        """
        all_data = []

        # 1. Dados de arquivos JSONL
        data_path = Path("data/ml_training")
        if data_path.exists():
            for file in data_path.glob("*.jsonl"):
                with open(file, "r") as f:
                    for line in f:
                        try:
                            all_data.append(json.loads(line))
                        except:
                            continue

        # 2. Dados do Memory Manager
        recent_conversations = self.memory.get_recent_ml_feedback(days=30)
        all_data.extend(recent_conversations)

        return all_data

    def _get_feature_names(self) -> List[str]:
        """
        Nomes das features para explicabilidade
        """
        return [
            "Score Total",
            "Score Preço",
            "Score Categoria",
            "Score Economia",
            "Score Opcionais",
            "Uso Score",
            "Razões Count",
            "Pontos Fortes",
            "Brand Valid",
            "Brand Confidence",
            "Messages",
            "Has Agent",
            "Interactions",
            "Preço",
            "Idade",
            "KM",
            "Consumo",
            "Cilindrada",
            "Porta-malas",
            "Lugares",
            "Segurança",
            "É SUV",
            "É Sedan",
            "É Hatch",
            "É Flex",
            "É Automático",
            "Orçamento",
            "Primeiro Carro",
            "Família Size",
            "KM/mês",
            "Ar Condicionado",
            "Direção",
            "Airbag",
            "ABS",
            "Android Auto",
            "Apple CarPlay",
            "Sensor",
            "Câmera",
            "Automático",
            "Couro",
            "Teto Solar",
            "Rodas",
        ]

    def _get_top_features(self, importances: np.ndarray, top_n: int = 5) -> List[str]:
        """
        Retorna top features mais importantes
        """
        feature_names = self._get_feature_names()
        top_idx = np.argsort(importances)[-top_n:][::-1]

        return [
            f"{feature_names[i]}: {importances[i]:.2%}"
            for i in top_idx
            if i < len(feature_names)
        ]

    def save_model(self):
        """
        Salva modelo e metadados
        """
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "is_trained": self.is_trained,
            "feature_names": self._get_feature_names(),
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "n_samples": len(self.model.estimators_[0].tree_.value)
                if self.model
                else 0,
                "n_features": len(self._get_feature_names()),
            },
        }

        with open(self.model_path, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"✅ Modelo salvo em {self.model_path}")

    def load_model(self) -> bool:
        """
        Carrega modelo salvo
        """
        if not self.model_path.exists():
            return False

        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.is_trained = model_data["is_trained"]

            logger.info(f"✅ Modelo carregado: {model_data['timestamp']}")
            logger.info(f"📊 Métricas: {model_data.get('metrics', {})}")

            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            return False


class SuperHybridProcessor:
    """
    Processador híbrido que integra TUDO
    """

    def __init__(self):
        # Todos os componentes existentes
        self.uso_matcher = UsoMatcher()
        self.memory = ConversationMemoryManager()
        self.brand_processor = EnhancedBrandProcessor()

        # Novos componentes ML
        self.ml_model = SmartMVPModel()
        self.collector = IntegratedMLCollector()

        # Configuração adaptativa
        self.ml_weight = self._calculate_ml_weight()
        self.min_confidence = 0.5

        logger.info(f"🚀 SuperHybrid inicializado - ML weight: {self.ml_weight:.0%}")

    def processar_recomendacao_completa(
        self,
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
        conversation_id: Optional[str] = None,
        user_session_id: Optional[str] = None,
        collect_data: bool = True,
    ) -> Dict[str, Any]:
        """
        Processa recomendação usando TODA inteligência disponível
        """
        start_time = datetime.now()

        # 1. Busca Inteligente (sistema existente)
        estado_busca: EstadoBuscaDict = {
            "questionario": questionario,
            "carros_disponiveis": [carro],
            "carros_filtrados": [carro],
            "pontuacoes": [],
            "recomendacoes_finais": [],
            "resumo_perfil": "",
            "sugestoes_personalizadas": [],
        }
        resultado_busca = calcular_scores_compatibilidade(estado_busca)
        busca_score = (
            resultado_busca["pontuacoes"][0]["score"]
            if resultado_busca.get("pontuacoes")
            else 0
        )

        # 2. Uso Principal (sistema existente)
        (
            uso_score,
            uso_razoes,
            uso_fortes,
        ) = self.uso_matcher.calcular_score_uso_principal(questionario, carro)

        # 3. Score combinado das regras
        rule_score = (busca_score * 0.6) + (uso_score * 0.4)

        # 4. ML Prediction (se disponível)
        ml_result = None
        ml_score = None
        ml_confidence = None

        if self.ml_model.is_trained:
            try:
                ml_result = self.ml_model.predict_smart(
                    carro, questionario, conversation_id
                )
                ml_score = ml_result["score"]
                ml_confidence = ml_result["confidence"]
            except Exception as e:
                logger.error(f"ML falhou: {e}")

        # 5. Calcular score final
        if ml_result and ml_confidence and ml_confidence >= self.min_confidence:
            # Combinação adaptativa
            final_score = (1 - self.ml_weight) * rule_score + self.ml_weight * ml_score
            method = "super_hybrid"
            confidence = ml_confidence
        else:
            final_score = rule_score
            method = "rules_enhanced"
            confidence = 0.7  # Confiança padrão para regras

        # 6. Coletar dados para ML (se habilitado)
        if collect_data:
            self.collector.collect_from_conversation(
                conversation_id=conversation_id,
                user_session_id=user_session_id,
                carro=carro,
                score=final_score,
                user_action=None,  # Será atualizado via API
                questionario=questionario,
                rule_score=rule_score,
                ml_score=ml_score,
                ml_confidence=ml_confidence,
                method=method,
            )

        # 7. Salvar no Memory Manager (simplificado por enquanto)
        # TODO: Integrar com persist_conversation_result quando houver mensagens reais
        # if conversation_id:
        #     self.memory.persist_conversation_result(...)

        # 8. Preparar resposta completa
        return {
            "score": final_score,
            "confidence": confidence,
            "method": method,
            "components": {
                "busca_score": busca_score,
                "uso_score": uso_score,
                "rule_score": rule_score,
                "ml_score": ml_score,
            },
            "explanations": {
                "principais": uso_razoes[:3],
                "pontos_fortes": uso_fortes[:3],
                "ml_insights": ml_result["explanations"] if ml_result else [],
            },
            "metadata": {
                "ml_trained": self.ml_model.is_trained,
                "ml_weight": self.ml_weight,
                "processing_time_ms": int(
                    (datetime.now() - start_time).total_seconds() * 1000
                ),
                "conversation_id": conversation_id,
            },
        }

    def _calculate_ml_weight(self) -> float:
        """
        Calcula peso do ML baseado em performance histórica
        """
        # Começar conservador
        base_weight = 0.2

        # Aumentar se modelo treinado
        if self.ml_model.is_trained:
            base_weight = 0.3

            # Verificar performance histórica no Memory Manager
            ml_stats = self.memory.get_ml_performance_stats()
            if ml_stats:
                accuracy = ml_stats.get("accuracy", 0)
                if accuracy > 0.8:
                    base_weight = 0.5
                elif accuracy > 0.7:
                    base_weight = 0.4

        return base_weight

    def treinar_modelo_com_feedback(self):
        """
        Treina modelo usando todo feedback coletado
        """
        logger.info("🎯 Iniciando treinamento com feedback...")

        # Treinar modelo
        success = self.ml_model.train_with_smart_data(min_samples=30)

        if success:
            # Ajustar peso do ML baseado em sucesso
            old_weight = self.ml_weight
            self.ml_weight = min(0.6, self.ml_weight + 0.1)

            logger.info(f"✅ Treinamento concluído!")
            logger.info(f"📈 ML weight: {old_weight:.0%} → {self.ml_weight:.0%}")

            # Salvar métricas no Memory Manager
            self.memory.save_ml_training_metrics(
                {
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "new_weight": self.ml_weight,
                    "model_path": str(self.ml_model.model_path),
                }
            )
        else:
            logger.warning("⚠️ Treinamento falhou - dados insuficientes")

        return success

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Estatísticas completas do sistema híbrido
        """
        # Buscar dados do Memory Manager
        conversation_stats = self.memory.get_conversation_analytics(days=7)
        # ML performance será calculado localmente por enquanto
        ml_performance = {
            "avg_confidence": self.ml_model.confidence_score
            if hasattr(self.ml_model, "confidence_score")
            else 0.0,
            "predictions_made": 0,  # TODO: implementar contador
            "feedback_received": 0,  # TODO: implementar contador
        }

        # Contar dados de treinamento
        data_path = Path("data/ml_training")
        total_samples = 0
        if data_path.exists():
            for file in data_path.glob("*.jsonl"):
                with open(file, "r") as f:
                    total_samples += sum(1 for _ in f)

        return {
            "system_status": {
                "ml_trained": self.ml_model.is_trained,
                "ml_weight": self.ml_weight,
                "min_confidence": self.min_confidence,
                "total_training_samples": total_samples,
                "ready_to_train": total_samples >= 30,
            },
            "conversation_metrics": conversation_stats,
            "ml_performance": ml_performance,
            "components_health": {
                "memory_manager": "✅ Active",
                "uso_matcher": "✅ Active",
                "ml_model": "✅ Active" if self.ml_model.is_trained else "⏳ Training",
                "collector": "✅ Active",
            },
            "next_training": {
                "samples_needed": max(0, 30 - total_samples),
                "estimated_time": f"{max(0, 30 - total_samples) * 2} hours",
            },
        }


# Singleton para uso global
_processor_instance = None


def get_hybrid_processor() -> SuperHybridProcessor:
    """
    Retorna instância singleton do processador híbrido
    """
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = SuperHybridProcessor()
    return _processor_instance
