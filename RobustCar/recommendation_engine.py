#!/usr/bin/env python3
"""
🤖 RobustCar Recommendation Engine
Agente Responsável: AI Engineer 🤖

Sistema de recomendação com guardrails específico para a RobustCar,
baseado no estoque real extraído via scraping.
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import math
from datetime import datetime
import logging

from robustcar_scraper import CarData

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Perfil do usuário baseado no questionário"""
    orcamento_min: float
    orcamento_max: float
    uso_principal: str  # trabalho, familia, lazer, primeiro_carro
    tamanho_familia: int
    prioridades: Dict[str, int]  # economia, espaco, performance, conforto, seguranca (1-5)
    marcas_preferidas: List[str]
    tipos_preferidos: List[str]  # hatch, sedan, suv
    combustivel_preferido: str
    idade_usuario: int
    experiencia_conducao: str  # iniciante, intermediario, experiente
    
@dataclass
class CarRecommendation:
    """Recomendação de carro com score e justificativa"""
    carro: CarData
    score: float
    justificativa: str
    pontos_fortes: List[str]
    pontos_atencao: List[str]
    match_percentage: int

class RobustCarRecommendationEngine:
    """
    Engine de recomendação com guardrails do AI Engineer
    """
    
    def __init__(self, estoque_file: str = None):
        self.estoque: List[CarData] = []
        self.guardrails = RecommendationGuardrails()
        
        if estoque_file:
            self.carregar_estoque(estoque_file)
    
    def carregar_estoque(self, estoque_file: str):
        """Carregar estoque a partir do arquivo JSON do scraper"""
        try:
            with open(estoque_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.estoque = []
            for item in dados:
                try:
                    # Reconstruir objeto CarData
                    carro = CarData(
                        id=item['id'],
                        nome=item['nome'],
                        marca=item['marca'],
                        modelo=item['modelo'],
                        ano=item['ano'],
                        preco=item['preco'],
                        quilometragem=item['quilometragem'],
                        combustivel=item['combustivel'],
                        cambio=item['cambio'],
                        cor=item['cor'],
                        descricao=item['descricao'],
                        imagens=item['imagens'],
                        url_original=item['url_original'],
                        data_scraping=item['data_scraping'],
                        disponivel=item.get('disponivel', True),
                        categoria=item.get('categoria', ''),
                        consumo_estimado=item.get('consumo_estimado', 0.0),
                        score_familia=item.get('score_familia', 0.0),
                        score_economia=item.get('score_economia', 0.0)
                    )
                    self.estoque.append(carro)
                    
                except Exception as e:
                    logger.warning(f"Erro ao carregar carro {item.get('id', 'unknown')}: {e}")
            
            logger.info(f"Estoque carregado: {len(self.estoque)} carros")
            
        except Exception as e:
            logger.error(f"Erro ao carregar estoque: {e}")
            self.estoque = []
    
    def recomendar(self, perfil: UserProfile, limite: int = 5) -> List[CarRecommendation]:
        """
        Gerar recomendações com guardrails
        """
        if not self.estoque:
            logger.warning("Estoque vazio - não é possível fazer recomendações")
            return []
        
        # 1. Aplicar filtros básicos (guardrails)
        carros_filtrados = self.aplicar_filtros_basicos(perfil)
        
        if not carros_filtrados:
            logger.warning("Nenhum carro disponível após filtros básicos")
            return self.recomendacoes_fallback(perfil, limite)
        
        # 2. Calcular scores para cada carro
        carros_com_score = []
        for carro in carros_filtrados:
            score = self.calcular_score(carro, perfil)
            
            if score > 0:  # Só incluir carros com score positivo
                carros_com_score.append((carro, score))
        
        # 3. Ordenar por score
        carros_com_score.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Gerar recomendações finais
        recomendacoes = []
        for carro, score in carros_com_score[:limite]:
            recomendacao = self.gerar_recomendacao(carro, score, perfil)
            
            # Aplicar guardrails finais
            if self.guardrails.validar_recomendacao(recomendacao, perfil):
                recomendacoes.append(recomendacao)
        
        # 5. Garantir pelo menos 3 recomendações se possível
        if len(recomendacoes) < 3 and len(carros_com_score) >= 3:
            recomendacoes = self.expandir_recomendacoes(carros_com_score, perfil, 3)
        
        logger.info(f"Geradas {len(recomendacoes)} recomendações para perfil {perfil.uso_principal}")
        return recomendacoes
    
    def aplicar_filtros_basicos(self, perfil: UserProfile) -> List[CarData]:
        """Aplicar filtros básicos de guardrails"""
        carros_filtrados = []
        
        for carro in self.estoque:
            # Filtro de orçamento (obrigatório)
            if not (perfil.orcamento_min <= carro.preco <= perfil.orcamento_max):
                continue
            
            # Filtro de disponibilidade
            if not carro.disponivel:
                continue
            
            # Filtro de ano (não muito antigo)
            if carro.ano < 2010:
                continue
            
            # Filtro de preço coerente (evitar outliers)
            if carro.preco < 5000 or carro.preco > 500000:
                continue
            
            carros_filtrados.append(carro)
        
        return carros_filtrados
    
    def calcular_score(self, carro: CarData, perfil: UserProfile) -> float:
        """Calcular score de compatibilidade carro-usuário"""
        score = 0.0
        
        # Score base por categoria e uso
        score += self.score_categoria_uso(carro, perfil) * 0.3
        
        # Score por prioridades do usuário
        score += self.score_prioridades(carro, perfil) * 0.4
        
        # Score por preferências (marca, tipo)
        score += self.score_preferencias(carro, perfil) * 0.2
        
        # Score por adequação ao orçamento
        score += self.score_orcamento(carro, perfil) * 0.1
        
        # Penalizar carros muito antigos ou com muito km
        score *= self.fator_condicao(carro)
        
        return min(score, 1.0)  # Normalizar entre 0 e 1
    
    def score_categoria_uso(self, carro: CarData, perfil: UserProfile) -> float:
        """Score baseado na categoria do carro vs uso"""
        uso_scores = {
            'familia': {
                'SUV': 0.9,
                'Sedan': 0.8,
                'Hatch': 0.6,
                'Pickup': 0.5
            },
            'trabalho': {
                'Hatch': 0.9,
                'Sedan': 0.7,
                'SUV': 0.4,
                'Pickup': 0.3
            },
            'lazer': {
                'SUV': 0.8,
                'Pickup': 0.7,
                'Sedan': 0.6,
                'Hatch': 0.5
            },
            'primeiro_carro': {
                'Hatch': 0.9,
                'Sedan': 0.6,
                'SUV': 0.3,
                'Pickup': 0.2
            }
        }
        
        categoria = carro.categoria
        uso = perfil.uso_principal
        
        return uso_scores.get(uso, {}).get(categoria, 0.5)
    
    def score_prioridades(self, carro: CarData, perfil: UserProfile) -> float:
        """Score baseado nas prioridades do usuário"""
        score = 0.0
        total_peso = sum(perfil.prioridades.values())
        
        if total_peso == 0:
            return 0.5
        
        for prioridade, peso in perfil.prioridades.items():
            peso_normalizado = peso / total_peso
            
            if prioridade == 'economia':
                # Score economia baseado no score pré-calculado e categoria
                score_item = carro.score_economia
                if carro.categoria == 'Hatch':
                    score_item += 0.1
                score += score_item * peso_normalizado
                
            elif prioridade == 'espaco':
                # Score espaço baseado na categoria
                score_espaco = {
                    'SUV': 0.9,
                    'Sedan': 0.7,
                    'Pickup': 0.8,
                    'Hatch': 0.4
                }.get(carro.categoria, 0.5)
                score += score_espaco * peso_normalizado
                
            elif prioridade == 'performance':
                # Score performance baseado no ano e categoria
                score_perf = min(0.9, (carro.ano - 2010) / 15)  # Mais novo = melhor
                if carro.categoria == 'Sedan':
                    score_perf += 0.1
                score += score_perf * peso_normalizado
                
            elif prioridade == 'conforto':
                # Score conforto baseado em ano e categoria
                score_conforto = min(0.9, (carro.ano - 2015) / 10)
                if carro.categoria in ['SUV', 'Sedan']:
                    score_conforto += 0.1
                score += score_conforto * peso_normalizado
                
            elif prioridade == 'seguranca':
                # Score segurança baseado no score família pré-calculado
                score += carro.score_familia * peso_normalizado
        
        return score
    
    def score_preferencias(self, carro: CarData, perfil: UserProfile) -> float:
        """Score baseado em preferências específicas"""
        score = 0.5  # Score base
        
        # Marca preferida
        if carro.marca in perfil.marcas_preferidas:
            score += 0.3
        
        # Tipo preferido
        if carro.categoria.lower() in [t.lower() for t in perfil.tipos_preferidos]:
            score += 0.2
        
        return min(score, 1.0)
    
    def score_orcamento(self, carro: CarData, perfil: UserProfile) -> float:
        """Score baseado na posição no orçamento"""
        range_orcamento = perfil.orcamento_max - perfil.orcamento_min
        posicao_carro = carro.preco - perfil.orcamento_min
        
        if range_orcamento == 0:
            return 1.0 if carro.preco == perfil.orcamento_min else 0.0
        
        # Score máximo no meio do orçamento
        posicao_normalizada = posicao_carro / range_orcamento
        
        if posicao_normalizada <= 0.5:
            return posicao_normalizada * 2  # 0 a 1
        else:
            return 2 * (1 - posicao_normalizada)  # 1 a 0
    
    def fator_condicao(self, carro: CarData) -> float:
        """Fator de penalização por condição do carro"""
        fator = 1.0
        
        # Penalizar carros muito antigos
        idade = 2024 - carro.ano
        if idade > 10:
            fator *= 0.8
        elif idade > 15:
            fator *= 0.6
        
        # Penalizar alta quilometragem
        if carro.quilometragem > 100000:
            fator *= 0.9
        elif carro.quilometragem > 200000:
            fator *= 0.7
        
        return fator
    
    def gerar_recomendacao(self, carro: CarData, score: float, perfil: UserProfile) -> CarRecommendation:
        """Gerar recomendação completa com justificativa"""
        
        # Gerar justificativa principal
        justificativa = self.gerar_justificativa(carro, perfil)
        
        # Identificar pontos fortes
        pontos_fortes = self.identificar_pontos_fortes(carro, perfil)
        
        # Identificar pontos de atenção
        pontos_atencao = self.identificar_pontos_atencao(carro, perfil)
        
        # Calcular porcentagem de match
        match_percentage = int(score * 100)
        
        return CarRecommendation(
            carro=carro,
            score=score,
            justificativa=justificativa,
            pontos_fortes=pontos_fortes,
            pontos_atencao=pontos_atencao,
            match_percentage=match_percentage
        )
    
    def gerar_justificativa(self, carro: CarData, perfil: UserProfile) -> str:
        """Gerar justificativa personalizada"""
        elementos = []
        
        # Justificativa por uso
        if perfil.uso_principal == 'familia':
            if carro.categoria == 'SUV':
                elementos.append(f"SUV ideal para família com {perfil.tamanho_familia} pessoas")
            elif carro.categoria == 'Sedan':
                elementos.append("Sedan espaçoso e confortável para família")
        
        elif perfil.uso_principal == 'trabalho':
            if carro.categoria == 'Hatch':
                elementos.append("Hatch econômico perfeito para uso diário")
            elementos.append("ótimo custo-benefício para deslocamentos urbanos")
        
        # Justificativa por economia
        if perfil.prioridades.get('economia', 0) >= 4:
            elementos.append(f"consumo estimado de {carro.consumo_estimado:.1f} km/l")
        
        # Justificativa por marca
        if carro.marca in perfil.marcas_preferidas:
            elementos.append(f"da sua marca preferida {carro.marca}")
        
        # Justificativa por ano
        if carro.ano >= 2020:
            elementos.append("modelo recente com tecnologias atuais")
        
        # Justificativa por preço
        preco_formatado = f"R$ {carro.preco:,.0f}".replace(',', '.')
        elementos.append(f"por {preco_formatado}")
        
        if len(elementos) >= 2:
            return f"Recomendado por ser {', '.join(elementos[:-1])} e {elementos[-1]}."
        elif elementos:
            return f"Recomendado por {elementos[0]}."
        else:
            return "Boa opção dentro do seu perfil e orçamento."
    
    def identificar_pontos_fortes(self, carro: CarData, perfil: UserProfile) -> List[str]:
        """Identificar pontos fortes do carro"""
        pontos = []
        
        if carro.ano >= 2020:
            pontos.append("Modelo recente")
        
        if carro.quilometragem < 50000:
            pontos.append("Baixa quilometragem")
        
        if carro.marca in ['Toyota', 'Honda', 'Hyundai']:
            pontos.append("Marca confiável")
        
        if carro.score_economia >= 0.7:
            pontos.append("Econômico")
        
        if carro.categoria == 'SUV':
            pontos.append("Espaçoso")
        
        if carro.combustivel == 'Flex':
            pontos.append("Motor Flex")
        
        return pontos[:4]  # Máximo 4 pontos
    
    def identificar_pontos_atencao(self, carro: CarData, perfil: UserProfile) -> List[str]:
        """Identificar pontos que merecem atenção"""
        pontos = []
        
        idade = 2024 - carro.ano
        if idade > 8:
            pontos.append(f"Carro de {idade} anos")
        
        if carro.quilometragem > 100000:
            pontos.append(f"Alta quilometragem ({carro.quilometragem:,} km)")
        
        # Verificar se está no limite superior do orçamento
        if carro.preco > perfil.orcamento_max * 0.9:
            pontos.append("Próximo ao limite do orçamento")
        
        # Avisos específicos por uso
        if perfil.uso_principal == 'primeiro_carro' and carro.categoria == 'SUV':
            pontos.append("SUV pode ser desafiador para iniciantes")
        
        return pontos[:3]  # Máximo 3 pontos
    
    def recomendacoes_fallback(self, perfil: UserProfile, limite: int) -> List[CarRecommendation]:
        """Recomendações fallback quando filtros são muito restritivos"""
        logger.info("Aplicando estratégia fallback")
        
        # Relaxar filtros gradualmente
        carros_relaxados = []
        
        # 1. Tentar expandir orçamento em 20%
        for carro in self.estoque:
            if (perfil.orcamento_min * 0.8 <= carro.preco <= perfil.orcamento_max * 1.2 
                and carro.disponivel):
                carros_relaxados.append(carro)
        
        if not carros_relaxados:
            # 2. Ignorar preferências, manter só orçamento ampliado
            carros_relaxados = [c for c in self.estoque 
                              if c.preco <= perfil.orcamento_max * 1.5 and c.disponivel]
        
        # Ordenar por ano (mais novos primeiro)
        carros_relaxados.sort(key=lambda c: c.ano, reverse=True)
        
        # Gerar recomendações simples
        recomendacoes = []
        for carro in carros_relaxados[:limite]:
            recomendacao = CarRecommendation(
                carro=carro,
                score=0.5,
                justificativa="Opção disponível próxima ao seu perfil",
                pontos_fortes=["Disponível no estoque"],
                pontos_atencao=["Verifique se atende suas necessidades"],
                match_percentage=50
            )
            recomendacoes.append(recomendacao)
        
        return recomendacoes
    
    def expandir_recomendacoes(self, carros_com_score: List[Tuple], perfil: UserProfile, minimo: int) -> List[CarRecommendation]:
        """Expandir lista para garantir mínimo de recomendações"""
        recomendacoes = []
        
        for carro, score in carros_com_score[:minimo]:
            recomendacao = self.gerar_recomendacao(carro, score, perfil)
            recomendacoes.append(recomendacao)
        
        return recomendacoes

class RecommendationGuardrails:
    """Guardrails específicos para recomendações"""
    
    def validar_recomendacao(self, recomendacao: CarRecommendation, perfil: UserProfile) -> bool:
        """Validar se recomendação atende aos guardrails"""
        
        carro = recomendacao.carro
        
        # Guardrail 1: Preço dentro do orçamento
        if not (perfil.orcamento_min <= carro.preco <= perfil.orcamento_max):
            return False
        
        # Guardrail 2: Score mínimo
        if recomendacao.score < 0.2:
            return False
        
        # Guardrail 3: Carro disponível
        if not carro.disponivel:
            return False
        
        # Guardrail 4: Não muito antigo para iniciantes
        if (perfil.uso_principal == 'primeiro_carro' and 
            (2024 - carro.ano) > 12):
            return False
        
        # Guardrail 5: Verificar coerência de dados
        if carro.preco <= 0 or carro.ano < 1990 or carro.ano > 2025:
            return False
        
        return True

def exemplo_uso():
    """Exemplo de uso do sistema de recomendação"""
    
    # Criar perfil de usuário
    perfil = UserProfile(
        orcamento_min=40000,
        orcamento_max=70000,
        uso_principal='familia',
        tamanho_familia=4,
        prioridades={
            'economia': 4,
            'espaco': 5,
            'seguranca': 5,
            'conforto': 3,
            'performance': 2
        },
        marcas_preferidas=['Toyota', 'Honda'],
        tipos_preferidos=['SUV', 'Sedan'],
        combustivel_preferido='Flex',
        idade_usuario=35,
        experiencia_conducao='intermediario'
    )
    
    # Criar engine (assumindo que arquivo existe)
    engine = RobustCarRecommendationEngine('robustcar_estoque_20241201_140000.json')
    
    # Gerar recomendações
    recomendacoes = engine.recomendar(perfil, limite=5)
    
    # Exibir resultados
    print("🚗 Recomendações para seu perfil:")
    print("="*50)
    
    for i, rec in enumerate(recomendacoes, 1):
        print(f"\n{i}. {rec.carro.nome}")
        print(f"   💰 R$ {rec.carro.preco:,.0f}".replace(',', '.'))
        print(f"   📊 Match: {rec.match_percentage}%")
        print(f"   📝 {rec.justificativa}")
        print(f"   ✅ Pontos fortes: {', '.join(rec.pontos_fortes)}")
        if rec.pontos_atencao:
            print(f"   ⚠️  Atenção: {', '.join(rec.pontos_atencao)}")

if __name__ == "__main__":
    exemplo_uso()
