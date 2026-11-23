import unittest

import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from code_base import *
from estruturas import *
import regras
import verificador

class TestVerificadorFechamento(unittest.TestCase):
    """Testes para a função verificar_fechamento."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    def test_ramo_vazio(self):
        ramo = Ramo(formulas=[])
        self.assertFalse(verificador.verificar_fechamento(ramo))

    def test_ramo_com_uma_formula(self):
        ramo = Ramo(formulas=[FormulaMarcada(self.P, True)])
        self.assertFalse(verificador.verificar_fechamento(ramo))

    def test_ramo_sem_contradicao_marcas_iguais(self):
        # T P e T Q não geram contradição
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.Q, True)
        ramo = Ramo(formulas=[f1, f2])
        self.assertFalse(verificador.verificar_fechamento(ramo))

    def test_ramo_mesma_formula_mesma_marca(self):
        # T P e T P não geram contradição
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.P, True)
        ramo = Ramo(formulas=[f1, f2])
        self.assertFalse(verificador.verificar_fechamento(ramo))

    def test_ramo_fechado_atomo_simples(self):
        # T P e F P fecham o ramo
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.P, False)
        ramo = Ramo(formulas=[f1, f2])
        self.assertTrue(verificador.verificar_fechamento(ramo))

    def test_ramo_fechado_com_outras_formulas_no_meio(self):
        # T P, T Q, F P -> fecha devido a T P e F P
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.Q, True)
        f3 = FormulaMarcada(self.P, False)
        ramo = Ramo(formulas=[f1, f2, f3])
        self.assertTrue(verificador.verificar_fechamento(ramo))

    def test_ramo_fechado_formula_composta(self):
        # T (P ^ Q) e F (P ^ Q) fecham o ramo
        comp1 = self.P & self.Q
        comp2 = self.P & self.Q
        f1 = FormulaMarcada(comp1, True)
        f2 = FormulaMarcada(comp2, False)
        ramo = Ramo(formulas=[f1, f2])
        self.assertTrue(verificador.verificar_fechamento(ramo))

    def test_ramo_aberto_com_formulas_compostas_diferentes(self):
        # T (P ^ Q) e F (P v Q) não fecham o ramo
        f1 = FormulaMarcada(self.P & self.Q, True)
        f2 = FormulaMarcada(self.P | self.Q, False)
        ramo = Ramo(formulas=[f1, f2])
        self.assertFalse(verificador.verificar_fechamento(ramo))


class TestExtrairContraexemplo(unittest.TestCase):
    """Testes para a função extrair_contraexemplo."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    def test_ramo_sem_variaveis(self):
        # Apenas fórmulas compostas
        f1 = FormulaMarcada(self.P & self.Q, True)
        ramo = Ramo(formulas=[f1])
        resultado = verificador.extrair_contraexemplo(ramo)
        self.assertEqual(resultado, {})

    def test_ramo_com_uma_variavel(self):
        # T P -> {'P': True}
        ramo = Ramo(formulas=[FormulaMarcada(self.P, True)])
        resultado = verificador.extrair_contraexemplo(ramo)
        self.assertEqual(resultado, {'P': True})

    def test_ramo_com_multiplas_variaveis(self):
        # T P, F Q, T R -> {'P': True, 'Q': False, 'R': True}
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.Q, False)
        f3 = FormulaMarcada(self.R, True)
        ramo = Ramo(formulas=[f1, f2, f3])
        resultado = verificador.extrair_contraexemplo(ramo)
        self.assertEqual(resultado, {'P': True, 'Q': False, 'R': True})

    def test_ignora_formulas_compostas_e_extrai_apenas_atomos(self):
        # T (P ^ Q), T P, F R -> apenas P e R devem entrar no dicionário
        f1 = FormulaMarcada(self.P & self.Q, True)
        f2 = FormulaMarcada(self.P, True)
        f3 = FormulaMarcada(self.R, False)
        ramo = Ramo(formulas=[f1, f2, f3])
        resultado = verificador.extrair_contraexemplo(ramo)
        self.assertEqual(resultado, {'P': True, 'R': False})

    def test_sobrescrita_em_caso_de_multiplas_ocorrencias(self):
        # Se houver mais de uma ocorrência da mesma variável, o último valor iterado prevalece
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.P, False)
        ramo = Ramo(formulas=[f1, f2])
        resultado = verificador.extrair_contraexemplo(ramo)
        self.assertEqual(resultado, {'P': False})


if __name__ == '__main__':
    unittest.main()
