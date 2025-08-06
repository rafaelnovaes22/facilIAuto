"""
🧪 Unit Tests - Pydantic Models
Testes para validação e estrutura dos modelos
"""

import pytest
from pydantic import ValidationError

from app.models import CarroRecomendacao, QuestionarioBusca, RespostaBusca


class TestQuestionarioBusca:
    """Testes para o modelo QuestionarioBusca"""

    def test_questionario_valido_completo(self):
        """Testa criação de questionário válido completo"""
        # Arrange & Act
        questionario = QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            marcas_alternativas=["HONDA", "VOLKSWAGEN"],
            modelos_alternativos=["Civic", "Jetta"],
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano", "viagem"],
            pessoas_transportar=4,
            criancas=True,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
            orcamento_min=50000,
            orcamento_max=80000,
        )

        # Assert
        assert questionario.marca_preferida == "TOYOTA"
        assert questionario.modelo_especifico == "Corolla"
        assert len(questionario.marcas_alternativas) == 2
        assert len(questionario.modelos_alternativos) == 2
        assert questionario.urgencia == "hoje_amanha"
        assert questionario.pessoas_transportar == 4
        assert questionario.criancas is True
        assert questionario.animais is False
        assert questionario.orcamento_min == 50000
        assert questionario.orcamento_max == 80000

    def test_questionario_valido_minimo(self):
        """Testa criação de questionário válido mínimo"""
        # Arrange & Act
        questionario = QuestionarioBusca(
            marca_preferida="sem_preferencia",
            modelo_especifico="aberto_opcoes",
            urgencia="sem_pressa",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="equilibrio",
        )

        # Assert
        assert questionario.marca_preferida == "sem_preferencia"
        assert questionario.modelo_especifico == "aberto_opcoes"
        assert questionario.marcas_alternativas == []
        assert questionario.modelos_alternativos == []
        assert questionario.orcamento_min is None
        assert questionario.orcamento_max is None

    def test_questionario_campos_obrigatorios(self):
        """Testa campos obrigatórios do questionário"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            QuestionarioBusca()

        # Verificar que há erros de validação
        assert len(exc_info.value.errors()) > 0

    def test_validador_marcas_alternativas_none(self):
        """Testa validador para marcas_alternativas None"""
        # Arrange & Act
        questionario = QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            marcas_alternativas=None,  # Deve ser convertido para []
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
        )

        # Assert
        assert questionario.marcas_alternativas == []

    def test_validador_modelos_alternativos_string(self):
        """Testa validador para modelos_alternativos como string"""
        # Arrange & Act
        questionario = QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            modelos_alternativos="Civic",  # String deve ser convertido para lista
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
        )

        # Assert
        assert questionario.modelos_alternativos == ["Civic"]

    def test_validador_string_vazia(self):
        """Testa validador com string vazia"""
        # Arrange & Act
        questionario = QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            marcas_alternativas="",  # String vazia deve ser []
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
        )

        # Assert
        assert questionario.marcas_alternativas == []


class TestCarroRecomendacao:
    """Testes para o modelo CarroRecomendacao"""

    def test_carro_recomendacao_valido(self):
        """Testa criação de recomendação válida"""
        # Arrange & Act
        carro = CarroRecomendacao(
            id="123",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=65000,
            km=25000,
            combustivel="Flex",
            cor="Branco",
            categoria="Sedan",
            score_compatibilidade=95.5,
            razoes_recomendacao=["Marca preferida", "Modelo específico"],
            pontos_fortes=["Econômico", "Confiável"],
            consideracoes=["Considere o consumo"],
            fotos=["foto1.jpg", "foto2.jpg"],
            descricao="Corolla 2022 em excelente estado",
        )

        # Assert
        assert carro.id == "123"
        assert carro.marca == "Toyota"
        assert carro.modelo == "Corolla"
        assert carro.score_compatibilidade == 95.5
        assert len(carro.razoes_recomendacao) == 2
        assert len(carro.pontos_fortes) == 2
        assert len(carro.fotos) == 2

    def test_carro_validador_listas_none(self):
        """Testa validadores que convertem None para lista vazia"""
        # Arrange & Act
        carro = CarroRecomendacao(
            id="123",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=65000,
            km=25000,
            combustivel="Flex",
            cor="Branco",
            categoria="Sedan",
            score_compatibilidade=95.5,
            razoes_recomendacao=None,  # Deve ser convertido para []
            pontos_fortes=None,  # Deve ser convertido para []
            consideracoes=None,  # Deve ser convertido para []
            fotos=None,  # Deve ser convertido para []
            descricao="Teste",
        )

        # Assert
        assert carro.razoes_recomendacao == []
        assert carro.pontos_fortes == []
        assert carro.consideracoes == []
        assert carro.fotos == []

    def test_carro_campos_obrigatorios(self):
        """Testa campos obrigatórios do carro"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            CarroRecomendacao()


class TestRespostaBusca:
    """Testes para o modelo RespostaBusca"""

    def test_resposta_busca_valida(self):
        """Testa criação de resposta válida"""
        # Arrange
        carro = CarroRecomendacao(
            id="123",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=65000,
            km=25000,
            combustivel="Flex",
            cor="Branco",
            categoria="Sedan",
            score_compatibilidade=95.5,
            razoes_recomendacao=["Teste"],
            pontos_fortes=["Teste"],
            consideracoes=["Teste"],
            fotos=["foto.jpg"],
            descricao="Teste",
        )

        # Act
        resposta = RespostaBusca(
            recomendacoes=[carro],
            resumo_perfil="Perfil de teste",
            sugestoes_gerais=["Sugestão 1", "Sugestão 2"],
        )

        # Assert
        assert len(resposta.recomendacoes) == 1
        assert resposta.resumo_perfil == "Perfil de teste"
        assert len(resposta.sugestoes_gerais) == 2

    def test_resposta_busca_vazia(self):
        """Testa resposta com valores padrão"""
        # Arrange & Act
        resposta = RespostaBusca()

        # Assert
        assert resposta.recomendacoes == []
        assert resposta.resumo_perfil == ""
        assert resposta.sugestoes_gerais == []
