"""
Guardrails Service for response validation and deduplication.

Implements content deduplication, repetition filters, automatic reformulation,
and style policies to ensure high-quality, non-repetitive responses.
"""

import hashlib
import re
from typing import List, Optional, Dict
from datetime import datetime
import logging

from ..models.session import SessionData

logger = logging.getLogger(__name__)


class GuardrailsService:
    """
    Serviço de Guardrails para validação e deduplicação de respostas.
    
    Funcionalidades:
    - Deduplicação por hash de conteúdo
    - Filtros de repetição (últimas N mensagens)
    - Reformulação automática de respostas duplicadas
    - Políticas de estilo (tom, formatação)
    """
    
    def __init__(self, max_recent_messages: int = 5):
        """
        Inicializa o GuardrailsService.
        
        Args:
            max_recent_messages: Número de mensagens recentes a verificar
        """
        self.max_recent_messages = max_recent_messages
        
        # Frases de reformulação para respostas duplicadas
        self.reformulation_prefixes = [
            "Como mencionei anteriormente:\n\n",
            "Conforme expliquei antes:\n\n",
            "Reiterando o que disse:\n\n",
            "Para esclarecer novamente:\n\n",
            "Repetindo a informação:\n\n",
        ]
        
        # Políticas de estilo
        self.style_policies = {
            "max_length": 1000,  # Máximo de caracteres por mensagem
            "min_length": 10,    # Mínimo de caracteres
            "max_emojis": 5,     # Máximo de emojis por mensagem
            "forbidden_words": [  # Palavras proibidas
                "spam", "scam", "fraude"
            ],
        }
        
        logger.info("Guardrails Service initialized")
    
    def hash_content(self, content: str) -> str:
        """
        Gera hash SHA-256 do conteúdo normalizado.
        
        Args:
            content: Conteúdo a ser hasheado
            
        Returns:
            Hash hexadecimal do conteúdo
        """
        # Normalizar conteúdo (remover espaços extras, lowercase)
        normalized = self._normalize_for_hash(content)
        
        # Gerar hash
        hash_obj = hashlib.sha256(normalized.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _normalize_for_hash(self, content: str) -> str:
        """
        Normaliza conteúdo para geração de hash consistente.
        
        Args:
            content: Conteúdo original
            
        Returns:
            Conteúdo normalizado
        """
        # Lowercase
        normalized = content.lower()
        
        # Remover emojis (para comparação de conteúdo textual)
        normalized = re.sub(r'[^\w\s.,!?-]', '', normalized)
        
        # Remover múltiplos espaços
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remover pontuação excessiva
        normalized = re.sub(r'([!?.]){2,}', r'\1', normalized)
        
        # Trim
        normalized = normalized.strip()
        
        return normalized
    
    def check_duplicate(
        self,
        response: str,
        session: SessionData
    ) -> tuple[bool, Optional[str]]:
        """
        Verifica se resposta é duplicada e retorna versão reformulada se necessário.
        
        Args:
            response: Resposta a ser verificada
            session: Sessão atual com histórico
            
        Returns:
            Tupla (is_duplicate, reformulated_response)
            - is_duplicate: True se é duplicada
            - reformulated_response: Resposta reformulada ou None
        """
        # Obter mensagens recentes do assistente
        recent_messages = session.memory.get_recent_messages(self.max_recent_messages)
        assistant_messages = [
            msg["content"] for msg in recent_messages
            if msg["role"] == "assistant"
        ]
        
        # Verificar duplicação exata
        if response in assistant_messages:
            logger.warning("Exact duplicate detected")
            reformulated = self._reformulate_response(response, method="prefix")
            return True, reformulated
        
        # Verificar duplicação por hash (conteúdo similar)
        response_hash = self.hash_content(response)
        
        for msg in assistant_messages:
            msg_hash = self.hash_content(msg)
            if response_hash == msg_hash:
                logger.warning("Content duplicate detected (by hash)")
                reformulated = self._reformulate_response(response, method="rephrase")
                return True, reformulated
        
        # Verificar similaridade alta (>80% de palavras em comum)
        for msg in assistant_messages:
            similarity = self._calculate_similarity(response, msg)
            if similarity > 0.8:
                logger.warning(f"High similarity detected: {similarity:.2%}")
                reformulated = self._reformulate_response(response, method="variation")
                return True, reformulated
        
        # Não é duplicada
        return False, None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos (Jaccard similarity).
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        # Normalizar e tokenizar
        words1 = set(self._normalize_for_hash(text1).split())
        words2 = set(self._normalize_for_hash(text2).split())
        
        # Calcular Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _reformulate_response(self, response: str, method: str = "prefix") -> str:
        """
        Reformula resposta duplicada.
        
        Args:
            response: Resposta original
            method: Método de reformulação (prefix, rephrase, variation)
            
        Returns:
            Resposta reformulada
        """
        if method == "prefix":
            # Adicionar prefixo de reformulação
            import random
            prefix = random.choice(self.reformulation_prefixes)
            return prefix + response
        
        elif method == "rephrase":
            # Reformular com variação
            return (
                "Deixa eu explicar de outra forma:\n\n" +
                response +
                "\n\nFicou mais claro agora?"
            )
        
        elif method == "variation":
            # Adicionar variação contextual
            return (
                response +
                "\n\nPosso esclarecer algum ponto específico?"
            )
        
        else:
            # Default: apenas adicionar nota
            return response + "\n\n_(Repetindo a informação)_"
    
    def apply_style_policies(self, response: str) -> tuple[bool, str, List[str]]:
        """
        Aplica políticas de estilo à resposta.
        
        Args:
            response: Resposta a ser validada
            
        Returns:
            Tupla (is_valid, corrected_response, violations)
            - is_valid: True se passou em todas as políticas
            - corrected_response: Resposta corrigida
            - violations: Lista de violações encontradas
        """
        violations = []
        corrected = response
        
        # Verificar comprimento mínimo
        if len(response) < self.style_policies["min_length"]:
            violations.append(f"Response too short ({len(response)} chars)")
            corrected = response + "\n\nPosso te ajudar com mais alguma coisa?"
        
        # Verificar comprimento máximo
        if len(response) > self.style_policies["max_length"]:
            violations.append(f"Response too long ({len(response)} chars)")
            # Truncar e adicionar indicação
            corrected = response[:self.style_policies["max_length"] - 50]
            corrected += "...\n\n_(Mensagem truncada. Posso detalhar algum ponto?)_"
        
        # Contar emojis
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', response))
        if emoji_count > self.style_policies["max_emojis"]:
            violations.append(f"Too many emojis ({emoji_count})")
            # Não corrigir automaticamente, apenas alertar
        
        # Verificar palavras proibidas
        for word in self.style_policies["forbidden_words"]:
            if word.lower() in response.lower():
                violations.append(f"Forbidden word detected: {word}")
                # Remover palavra
                corrected = re.sub(
                    rf'\b{word}\b',
                    '[REMOVIDO]',
                    corrected,
                    flags=re.IGNORECASE
                )
        
        # Verificar formatação básica
        if not self._has_proper_formatting(response):
            violations.append("Poor formatting detected")
            corrected = self._improve_formatting(corrected)
        
        is_valid = len(violations) == 0
        
        if violations:
            logger.warning(f"Style policy violations: {violations}")
        
        return is_valid, corrected, violations
    
    def _has_proper_formatting(self, text: str) -> bool:
        """
        Verifica se texto tem formatação adequada.
        
        Args:
            text: Texto a verificar
            
        Returns:
            True se formatação é adequada
        """
        # Verificar se tem parágrafos (quebras de linha)
        has_paragraphs = '\n' in text
        
        # Verificar se não tem linhas muito longas (>150 chars)
        lines = text.split('\n')
        has_reasonable_lines = all(len(line) <= 150 for line in lines)
        
        # Verificar se começa com letra maiúscula
        starts_with_capital = text[0].isupper() if text else False
        
        return has_paragraphs and has_reasonable_lines and starts_with_capital
    
    def _improve_formatting(self, text: str) -> str:
        """
        Melhora formatação do texto.
        
        Args:
            text: Texto original
            
        Returns:
            Texto com formatação melhorada
        """
        # Garantir primeira letra maiúscula
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Adicionar quebras de linha em sentenças longas
        sentences = re.split(r'([.!?])\s+', text)
        formatted_sentences = []
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            formatted_sentences.append(sentence)
            
            # Adicionar quebra de linha a cada 2-3 sentenças
            if (len(formatted_sentences) % 3 == 0 and
                i + 2 < len(sentences)):
                formatted_sentences.append('\n')
        
        return ' '.join(formatted_sentences)
    
    def filter_repetitive_patterns(self, response: str) -> str:
        """
        Remove padrões repetitivos da resposta.
        
        Args:
            response: Resposta original
            
        Returns:
            Resposta sem repetições
        """
        # Remover palavras repetidas consecutivas
        # Ex: "muito muito bom" -> "muito bom"
        filtered = re.sub(r'\b(\w+)\s+\1\b', r'\1', response, flags=re.IGNORECASE)
        
        # Remover frases repetidas
        sentences = filtered.split('.')
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            normalized = sentence.strip().lower()
            if normalized and normalized not in seen:
                unique_sentences.append(sentence)
                seen.add(normalized)
        
        filtered = '.'.join(unique_sentences)
        
        # Remover múltiplas quebras de linha
        filtered = re.sub(r'\n{3,}', '\n\n', filtered)
        
        return filtered.strip()
    
    def validate_response(
        self,
        response: str,
        session: SessionData
    ) -> tuple[str, Dict[str, any]]:
        """
        Valida resposta aplicando todos os guardrails.
        
        Este é o método principal que aplica todas as verificações:
        - Deduplicação
        - Políticas de estilo
        - Filtros de repetição
        
        Args:
            response: Resposta a ser validada
            session: Sessão atual
            
        Returns:
            Tupla (validated_response, metadata)
            - validated_response: Resposta validada e corrigida
            - metadata: Metadados sobre validação (duplicates, violations, etc)
        """
        metadata = {
            "original_length": len(response),
            "is_duplicate": False,
            "style_violations": [],
            "was_reformulated": False,
            "timestamp": datetime.now().isoformat()
        }
        
        validated = response
        
        # 1. Verificar duplicação
        is_duplicate, reformulated = self.check_duplicate(validated, session)
        if is_duplicate and reformulated:
            validated = reformulated
            metadata["is_duplicate"] = True
            metadata["was_reformulated"] = True
        
        # 2. Filtrar padrões repetitivos
        validated = self.filter_repetitive_patterns(validated)
        
        # 3. Aplicar políticas de estilo
        is_valid, corrected, violations = self.apply_style_policies(validated)
        if not is_valid:
            validated = corrected
            metadata["style_violations"] = violations
        
        # 4. Verificar se resposta está vazia após validações
        if not validated or validated.strip() == "":
            validated = (
                "Desculpe, não consegui formular uma resposta adequada. 🤔\n\n"
                "Pode reformular sua pergunta?"
            )
            metadata["was_reformulated"] = True
        
        metadata["final_length"] = len(validated)
        
        logger.info(
            f"Response validated: "
            f"duplicate={metadata['is_duplicate']}, "
            f"violations={len(metadata['style_violations'])}, "
            f"reformulated={metadata['was_reformulated']}"
        )
        
        return validated, metadata


# Função auxiliar para criar instância do serviço
def create_guardrails_service(max_recent_messages: int = 5) -> GuardrailsService:
    """
    Factory function para criar GuardrailsService.
    
    Args:
        max_recent_messages: Número de mensagens recentes a verificar
        
    Returns:
        GuardrailsService inicializado
    """
    return GuardrailsService(max_recent_messages)
