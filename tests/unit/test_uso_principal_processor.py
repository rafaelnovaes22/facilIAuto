"""
Testes unitários para o processador de uso principal do veículo
"""

import pytest
from app.models import QuestionarioBusca
from app.uso_principal_processor import UsoMatcher


class TestUsoMatcher:
    """Testes para a classe UsoMatcher"""
    
    def test_calcular_score_uso_urbano(self):
        """Testa o cálculo de score para uso urbano"""
        questionario = QuestionarioBusca(
            marca_preferida="Toyota",
            modelo_especifico="Corolla",
            urgencia="sem_pressa",
            regiao="São Paulo",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            espaco_carga="medio",
            potencia_desejada="economica",
            prioridade="economia"
        )
        
        carro = {
            "id": "1",
            "marca": "Toyota",
            "modelo": "Corolla",
            "categoria": "Hatch",
            "potencia_desejada": "economica",
            "opcionais": ["Conectividade Bluetooth", "Câmera de ré"],
            "ano": 2020,
            "preco": 50000
        }
        
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Deve ter score positivo para uso urbano
        assert score > 0
        assert len(razoes) > 0
        assert len(pontos_fortes) > 0
        assert any("urbano" in razao.lower() for razao in razoes)
    
    def test_calcular_score_uso_viagem(self):
        """Testa o cálculo de score para viagens"""
        questionario = QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="CR-V",
            urgencia="sem_pressa",
            regiao="Rio de Janeiro",
            uso_principal=["viagem"],
            pessoas_transportar=5,
            espaco_carga="muito",
            potencia_desejada="media",
            prioridade="conforto"
        )
        
        carro = {
            "id": "2",
            "marca": "Honda",
            "modelo": "CR-V",
            "categoria": "SUV",
            "potencia_desejada": "media",
            "espaco_carga": "muito",
            "seguranca": 5,
            "opcionais": ["Ar condicionado", "Direção assistida"],
            "ano": 2021,
            "preco": 80000
        }
        
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Deve ter score alto para SUV em viagens
        assert score > 0
        assert any("viagem" in razao.lower() for razao in razoes)
        assert any("espaço" in ponto.lower() or "conforto" in ponto.lower() for ponto in pontos_fortes)
    
    def test_calcular_score_uso_trabalho(self):
        """Testa o cálculo de score para trabalho"""
        questionario = QuestionarioBusca(
            marca_preferida="Ford",
            modelo_especifico="Ranger",
            urgencia="esta_semana",
            regiao="Brasília",
            uso_principal=["trabalho"],
            pessoas_transportar=4,
            espaco_carga="muito",
            potencia_desejada="alta",
            prioridade="equilibrio"
        )
        
        carro = {
            "id": "3",
            "marca": "Ford",
            "modelo": "Ranger",
            "categoria": "Pickup",
            "potencia_desejada": "alta",
            "espaco_carga": "muito",
            "km": 50000,
            "ano": 2019,
            "preco": 120000
        }
        
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Pickup deve ter score alto para trabalho
        assert score > 0
        assert any("trabalho" in razao.lower() for razao in razoes)
        assert any("carga" in ponto.lower() or "profissional" in ponto.lower() for ponto in pontos_fortes)
    
    def test_calcular_score_uso_familia(self):
        """Testa o cálculo de score para família"""
        questionario = QuestionarioBusca(
            marca_preferida="Chevrolet",
            modelo_especifico="Spin",
            urgencia="ate_15_dias",
            regiao="Salvador",
            uso_principal=["familia"],
            pessoas_transportar=7,
            criancas=True,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="seguranca"
        )
        
        carro = {
            "id": "4",
            "marca": "Chevrolet",
            "modelo": "Spin",
            "categoria": "SUV",
            "capacidade_pessoas": 7,
            "seguranca": 4,
            "opcionais": ["Ar condicionado", "Vidros elétricos", "Airbags"],
            "ano": 2020,
            "preco": 65000
        }
        
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Deve ter score alto para uso familiar
        assert score > 0
        assert any("familia" in razao.lower() for razao in razoes)
        assert any("família" in ponto.lower() or "segurança" in ponto.lower() for ponto in pontos_fortes)
    
    def test_uso_multiplo(self):
        """Testa o cálculo de score para múltiplos usos"""
        questionario = QuestionarioBusca(
            marca_preferida="Volkswagen",
            modelo_especifico="Tiguan",
            urgencia="sem_pressa",
            regiao="Porto Alegre",
            uso_principal=["urbano", "familia", "viagem"],
            pessoas_transportar=5,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="equilibrio"
        )
        
        carro = {
            "id": "5",
            "marca": "Volkswagen",
            "modelo": "Tiguan",
            "categoria": "SUV Médio",
            "capacidade_pessoas": 5,
            "seguranca": 5,
            "espaco_carga": "medio",
            "potencia_desejada": "media",
            "opcionais": ["Conectividade", "Ar condicionado", "Sensores"],
            "ano": 2021,
            "preco": 90000
        }
        
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Deve ter score dividido entre os usos
        assert score > 0
        assert len(razoes) >= 3  # Pelo menos uma razão por uso
        
        # Deve mencionar diferentes tipos de uso
        razoes_texto = " ".join(razoes).lower()
        assert "urbano" in razoes_texto or "família" in razoes_texto or "viagem" in razoes_texto
    
    def test_gerar_sugestoes_uso(self):
        """Testa a geração de sugestões baseadas no uso"""
        questionario = QuestionarioBusca(
            marca_preferida="Nissan",
            modelo_especifico="March",
            urgencia="hoje_amanha",
            regiao="Recife",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            espaco_carga="pouco",
            potencia_desejada="economica",
            prioridade="economia"
        )
        
        sugestoes = UsoMatcher.gerar_sugestoes_uso(questionario)
        
        assert len(sugestoes) > 0
        assert any("urbano" in sugestao.lower() for sugestao in sugestoes)
        # Não deve ter duplicatas
        assert len(sugestoes) == len(set(sugestoes))
    
    def test_get_criterios_por_uso(self):
        """Testa a obtenção de critérios por tipo de uso"""
        criterios_urbano = UsoMatcher.get_criterios_por_uso("urbano")
        criterios_viagem = UsoMatcher.get_criterios_por_uso("trabalho")
        criterios_invalido = UsoMatcher.get_criterios_por_uso("invalido")
        
        assert len(criterios_urbano) > 0
        assert len(criterios_viagem) > 0
        assert len(criterios_invalido) == 0
        
        # Verificar estrutura dos critérios
        assert "dimensoes_compactas" in criterios_urbano
        assert "peso" in criterios_urbano["dimensoes_compactas"]
    
    def test_get_descricao_uso(self):
        """Testa a obtenção de descrições de uso"""
        desc_urbano = UsoMatcher.get_descricao_uso("urbano")
        desc_familia = UsoMatcher.get_descricao_uso("familia")
        desc_invalido = UsoMatcher.get_descricao_uso("invalido")
        
        assert "cidade" in desc_urbano.lower()
        assert "família" in desc_familia.lower() or "familiar" in desc_familia.lower()
        assert desc_invalido == "invalido"  # Fallback para o próprio termo
    
    def test_peso_uso_principal_limite(self):
        """Testa se o peso total do uso principal respeita o limite"""
        questionario = QuestionarioBusca(
            marca_preferida="BMW",
            modelo_especifico="X1",
            urgencia="sem_pressa",
            regiao="Curitiba",
            uso_principal=["urbano", "viagem", "trabalho", "familia"],  # Todos os usos
            pessoas_transportar=5,
            espaco_carga="medio",
            potencia_desejada="alta",
            prioridade="performance"
        )
        
        carro = {
            "id": "6",
            "marca": "BMW",
            "modelo": "X1",
            "categoria": "SUV",
            "capacidade_pessoas": 5,
            "seguranca": 5,
            "espaco_carga": "medio",
            "potencia_desejada": "alta",
            "opcionais": ["Conectividade premium", "Ar condicionado", "Couro"],
            "ano": 2022,
            "preco": 150000
        }
        
        score, _, _ = UsoMatcher.calcular_score_uso_principal(questionario, carro)
        
        # Score não deve exceder o peso máximo configurado
        assert score <= UsoMatcher.PESO_USO_PRINCIPAL