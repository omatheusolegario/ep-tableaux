import unittest
from unittest.mock import MagicMock, call, patch

import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from code_base import ArgumentForm, vars
from estruturas import EstadoTableau, EventoHistorico, FormulaMarcada, Ramo, ResultadoTableau
import motor


class TestMotorResolver(unittest.TestCase):
    """Testes unitários para a função resolver(argumento) do módulo motor.py."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    @patch('motor.iniciar')
    @patch('motor.verificar_fechamento')
    @patch('motor.registrar_evento')
    def test_ramo_inicial_ja_fecha(self, mock_registrar, mock_verificar, mock_iniciar):
        """Caso o ramo inicial já contenha contradição imediata (ex: T(P) e F(P))."""
        f_p_t = FormulaMarcada(self.P, True)
        f_p_f = FormulaMarcada(self.P, False)
        ramo_inicial = Ramo(formulas=[f_p_t, f_p_f], expandidos=set())
        mock_iniciar.return_value = ramo_inicial
        mock_verificar.return_value = True

        arg = ArgumentForm(self.P, conclusion=self.P)
        resultado = motor.resolver(arg)

        mock_iniciar.assert_called_once_with(arg)
        mock_verificar.assert_called_once_with(ramo_inicial)
        mock_registrar.assert_called_once_with(unittest.mock.ANY, ramo_inicial, "fechamento")

        self.assertIsInstance(resultado, ResultadoTableau)
        self.assertTrue(resultado.valido)

    @patch('motor.iniciar')
    @patch('motor.verificar_fechamento')
    @patch('motor.selecionar_formula')
    @patch('motor.extrair_contraexemplo')
    @patch('motor.registrar_evento')
    def test_ramo_satura_sem_fechar_invalido(
        self, mock_registrar, mock_extrair, mock_selecionar, mock_verificar, mock_iniciar
    ):
        """Quando não há fórmulas para expandir e não há contradição (ramo saturado e aberto)."""
        f_p = FormulaMarcada(self.P, True)
        f_q = FormulaMarcada(self.Q, False)
        ramo_inicial = Ramo(formulas=[f_p, f_q], expandidos=set())
        
        mock_iniciar.return_value = ramo_inicial
        mock_verificar.return_value = False
        mock_selecionar.return_value = (None, None)
        mock_extrair.return_value = {'P': True, 'Q': False}

        arg = ArgumentForm(self.P, conclusion=self.Q)
        resultado = motor.resolver(arg)

        mock_registrar.assert_called_once_with(unittest.mock.ANY, ramo_inicial, "saturacao")
        mock_extrair.assert_called_once_with(ramo_inicial)
        
        self.assertIsInstance(resultado, ResultadoTableau)
        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.contraexemplo, {'P': True, 'Q': False})
        self.assertIs(resultado.ramo_aberto, ramo_inicial)

    @patch('motor.iniciar')
    @patch('motor.verificar_fechamento')
    @patch('motor.selecionar_formula')
    @patch('motor.aplicar_regra')
    @patch('motor.registrar_evento')
    def test_expansao_regra_alpha_permanece_no_mesmo_ramo(
        self, mock_registrar, mock_aplicar, mock_selecionar, mock_verificar, mock_iniciar
    ):
        """Regra alpha deve manter o fluxo no laço interno (mesmo ramo), estendendo fórmulas."""
        f_and = FormulaMarcada(self.P & self.Q, True)
        ramo_inicial = Ramo(formulas=[f_and], expandidos=set())
        mock_iniciar.return_value = ramo_inicial

        f_p = FormulaMarcada(self.P, True)
        f_q = FormulaMarcada(self.Q, True)
        mock_aplicar.return_value = [[f_p, f_q]]

        # Passos do laço interno:
        # 1ª iteração: verificar_fechamento -> False
        #              selecionar_formula -> (f_and, "alpha_and")
        #              aplica regra, adiciona subfórmulas e id aos expandidos
        # 2ª iteração: verificar_fechamento -> True (simulando fechamento com novas fórmulas)
        mock_verificar.side_effect = [False, True]
        mock_selecionar.return_value = (f_and, "alpha_and")

        arg = ArgumentForm(self.P & self.Q, conclusion=self.P)
        resultado = motor.resolver(arg)

        self.assertTrue(resultado.valido)
        self.assertIn(f_and.id, ramo_inicial.expandidos)
        self.assertIn(f_p, ramo_inicial.formulas)
        self.assertIn(f_q, ramo_inicial.formulas)
        mock_registrar.assert_has_calls([
            call(
                unittest.mock.ANY,
                ramo_inicial,
                "expansao",
                formula=f_and,
                nome_regra="alpha_and",
                expansao="alpha",
                geradas=[[f_p, f_q]],
            ),
            call(unittest.mock.ANY, ramo_inicial, "fechamento"),
        ])

    @patch('motor.iniciar')
    @patch('motor.verificar_fechamento')
    @patch('motor.selecionar_formula')
    @patch('motor.aplicar_regra')
    @patch('motor.registrar_evento')
    def test_expansao_regra_beta_bifurca_ramos_com_fechamento(
        self, mock_registrar, mock_aplicar, mock_selecionar, mock_verificar, mock_iniciar
    ):
        """Regra beta deve criar cópias dos ramos e colocar na pilha pendente."""
        f_or = FormulaMarcada(self.P | self.Q, True)
        ramo_inicial = Ramo(formulas=[f_or], expandidos=set())
        mock_iniciar.return_value = ramo_inicial

        f_p = FormulaMarcada(self.P, True)
        f_q = FormulaMarcada(self.Q, True)
        # Regra beta gera alternativas [[f_p], [f_q]]
        mock_aplicar.return_value = [[f_p], [f_q]]

        # 1ª vez: ramo_inicial não fecha -> seleciona beta_or
        # 2ª vez: primeiro filho popado fecha
        # 3ª vez: segundo filho popado fecha
        mock_verificar.side_effect = [False, True, True]
        mock_selecionar.return_value = (f_or, "beta_or")

        arg = ArgumentForm(self.P | self.Q, conclusion=self.P)
        resultado = motor.resolver(arg)

        self.assertTrue(resultado.valido)
        # Registra a expansão beta com expansao="beta"
        mock_registrar.assert_any_call(
            unittest.mock.ANY,
            ramo_inicial,
            "expansao",
            formula=f_or,
            nome_regra="beta_or",
            expansao="beta",
            geradas=[[f_p], [f_q]],
        )
        # Como houve mais de 1 ramo, os subsequentes disparam evento "retorno"
        mock_registrar.assert_any_call(unittest.mock.ANY, unittest.mock.ANY, "retorno")

    @patch('motor.iniciar')
    @patch('motor.verificar_fechamento')
    @patch('motor.selecionar_formula')
    @patch('motor.aplicar_regra')
    @patch('motor.extrair_contraexemplo')
    @patch('motor.registrar_evento')
    def test_expansao_beta_com_um_ramo_aberto(
        self, mock_registrar, mock_extrair, mock_aplicar, mock_selecionar, mock_verificar, mock_iniciar
    ):
        """Se após a bifurcação um ramo saturar sem fechar, a busca deve interromper e retornar inválido."""
        f_or = FormulaMarcada(self.P | self.Q, True)
        ramo_inicial = Ramo(formulas=[f_or], expandidos=set())
        mock_iniciar.return_value = ramo_inicial

        f_p = FormulaMarcada(self.P, True)
        f_q = FormulaMarcada(self.Q, True)
        mock_aplicar.return_value = [[f_p], [f_q]]

        # Ramo raiz: não fecha -> aplica beta
        # Filho 1: não fecha -> satura (seleciona None)
        mock_verificar.side_effect = [False, False]
        mock_selecionar.side_effect = [(f_or, "beta_or"), (None, None)]
        mock_extrair.return_value = {'P': False, 'Q': True}

        arg = ArgumentForm(self.P | self.Q, conclusion=self.R)
        resultado = motor.resolver(arg)

        self.assertFalse(resultado.valido)
        self.assertEqual(resultado.contraexemplo, {'P': False, 'Q': True})
        mock_registrar.assert_any_call(unittest.mock.ANY, unittest.mock.ANY, "saturacao")


class TestMotorIntegracaoPontaaPonta(unittest.TestCase):
    """Testes de ponta a ponta sem mocks, verificando a resolução completa de argumentos."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    def test_modus_ponens_valido(self):
        # P, P -> Q ⊢ Q (Válido)
        arg = ArgumentForm(self.P, self.P >> self.Q, conclusion=self.Q)
        resultado = motor.resolver(arg)

        self.assertTrue(resultado.valido)
        self.assertIsInstance(resultado.historico, list)
        self.assertGreater(len(resultado.historico), 0)

    def test_afirmacao_do_consequente_invalido(self):
        # Q, P -> Q ⊢ P (Inválido)
        arg = ArgumentForm(self.Q, self.P >> self.Q, conclusion=self.P)
        resultado = motor.resolver(arg)

        self.assertFalse(resultado.valido)
        self.assertIsNotNone(resultado.contraexemplo)
        self.assertIn('P', resultado.contraexemplo)
        self.assertFalse(resultado.contraexemplo['P'])
        self.assertIsInstance(resultado.ramo_aberto, Ramo)

    def test_lei_de_de_morgan_valida(self):
        # ~(P v Q) ⊢ ~P & ~Q (Válido)
        arg = ArgumentForm(~(self.P | self.Q), conclusion=(~self.P) & (~self.Q))
        resultado = motor.resolver(arg)

        self.assertTrue(resultado.valido)

    def test_disjuncao_simples_invalida(self):
        # P v Q ⊢ P (Inválido, contraexemplo com Q=True, P=False)
        arg = ArgumentForm(self.P | self.Q, conclusion=self.P)
        resultado = motor.resolver(arg)

        self.assertFalse(resultado.valido)
        self.assertIsNotNone(resultado.contraexemplo)


if __name__ == '__main__':
    unittest.main()
