import unittest

import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from code_base import Variable, And, Or, Implies, Not, vars
from estruturas import FormulaMarcada, Ramo
import seletor

class TestClassificar(unittest.TestCase):
    """Testes para a função classificar(formula: FormulaMarcada)."""

    def setUp(self):
        self.P, self.Q = vars('P', 'Q')

    def test_classificar_and(self):
        # T (P ^ Q) -> alpha_and | F (P ^ Q) -> beta_and
        fm_t = FormulaMarcada(self.P & self.Q, True)
        fm_f = FormulaMarcada(self.P & self.Q, False)
        self.assertEqual(seletor.classificar(fm_t), "alpha_and")
        self.assertEqual(seletor.classificar(fm_f), "beta_and")

    def test_classificar_or(self):
        # T (P v Q) -> beta_or | F (P v Q) -> alpha_or
        fm_t = FormulaMarcada(self.P | self.Q, True)
        fm_f = FormulaMarcada(self.P | self.Q, False)
        self.assertEqual(seletor.classificar(fm_t), "beta_or")
        self.assertEqual(seletor.classificar(fm_f), "alpha_or")

    def test_classificar_implies(self):
        # T (P => Q) -> beta_implies | F (P => Q) -> alpha_implies
        fm_t = FormulaMarcada(self.P >> self.Q, True)
        fm_f = FormulaMarcada(self.P >> self.Q, False)
        self.assertEqual(seletor.classificar(fm_t), "beta_implies")
        self.assertEqual(seletor.classificar(fm_f), "alpha_implies")

    def test_classificar_not(self):
        # T (~P) -> alpha_not | F (~P) -> beta_not
        fm_t = FormulaMarcada(~self.P, True)
        fm_f = FormulaMarcada(~self.P, False)
        self.assertEqual(seletor.classificar(fm_t), "alpha_not")
        self.assertEqual(seletor.classificar(fm_f), "beta_not")

    def test_classificar_atomos_retorna_none(self):
        # Literais não sofrem expansão
        fm_t = FormulaMarcada(self.P, True)
        fm_f = FormulaMarcada(self.P, False)
        self.assertIsNone(seletor.classificar(fm_t))
        self.assertIsNone(seletor.classificar(fm_f))


class TestTamanho(unittest.TestCase):
    """Testes para a função interna _tamanho(proposicao)."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    def test_tamanho_atomo(self):
        # Um átomo tem tamanho 1 (sem filhos)
        self.assertEqual(seletor._tamanho(self.P), 1)

    def test_tamanho_not(self):
        # ~P -> Not com 1 filho (P): 1 + 1 = 2
        self.assertEqual(seletor._tamanho(~self.P), 2)

    def test_tamanho_operador_binario(self):
        # P & Q -> And com 2 filhos (P, Q): 1 + 1 + 1 = 3
        self.assertEqual(seletor._tamanho(self.P & self.Q), 3)

    def test_tamanho_formula_composta(self):
        # (P v Q) >> ~R
        # Or(P, Q) -> 3 nós; Not(R) -> 2 nós; Implies(...) -> 1 + 3 + 2 = 6
        formula = (self.P | self.Q) >> (~self.R)
        self.assertEqual(seletor._tamanho(formula), 6)


class TestSelecionarFormula(unittest.TestCase):
    """Testes para a função selecionar_formula(ramo: Ramo)."""

    def setUp(self):
        self.P, self.Q, self.R, self.S = vars('P', 'Q', 'R', 'S')

    def test_ramo_vazio(self):
        ramo = Ramo(formulas=[], expandidos=set())
        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertIsNone(formula)
        self.assertIsNone(tipo)

    def test_ramo_apenas_com_atomos(self):
        # Átomos não são fórmulas alpha nem beta, logo nada deve ser selecionado
        f1 = FormulaMarcada(self.P, True)
        f2 = FormulaMarcada(self.Q, False)
        ramo = Ramo(formulas=[f1, f2], expandidos=set())

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertIsNone(formula)
        self.assertIsNone(tipo)

    def test_seleciona_alpha_imediatamente(self):
        # Regra alpha encontrada deve ser retornada de pronto
        f_alpha = FormulaMarcada(self.P & self.Q, True)  # alpha_and
        ramo = Ramo(formulas=[f_alpha], expandidos=set())

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertEqual(formula, f_alpha)
        self.assertEqual(tipo, "alpha_and")

    def test_prioridade_alpha_sobre_beta(self):
        # Regras alpha têm prioridade estrita sobre regras beta
        f_beta = FormulaMarcada(self.P | self.Q, True)   # beta_or
        f_alpha = FormulaMarcada(self.R >> self.S, False) # alpha_implies
        ramo = Ramo(formulas=[f_beta, f_alpha], expandidos=set())

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertEqual(formula, f_alpha)
        self.assertEqual(tipo, "alpha_implies")

    def test_ignora_formulas_ja_expandidas(self):
        # Fórmulas cujo id está em ramo.expandidos devem ser puladas
        f_alpha = FormulaMarcada(self.P & self.Q, True)
        f_beta = FormulaMarcada(self.R | self.S, True)
        ramo = Ramo(formulas=[f_alpha, f_beta], expandidos={f_alpha.id})

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertEqual(formula, f_beta)
        self.assertEqual(tipo, "beta_or")

    def test_todas_expandidas_retorna_none(self):
        f_alpha = FormulaMarcada(self.P & self.Q, True)
        f_beta = FormulaMarcada(self.R | self.S, True)
        ramo = Ramo(formulas=[f_alpha, f_beta], expandidos={f_alpha.id, f_beta.id})

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertIsNone(formula)
        self.assertIsNone(tipo)

    def test_desempate_beta_pelo_menor_tamanho(self):
        # Quando só há regras beta disponíveis, escolhe a de menor tamanho sintático
        # beta_maior: T ((P v Q) v (R v S)) -> tamanho > 3
        # beta_menor: T (P v Q) -> tamanho 3
        beta_maior = FormulaMarcada((self.P | self.Q) | (self.R | self.S), True)
        beta_menor = FormulaMarcada(self.P | self.Q, True)

        # Inserindo a maior antes da menor para testar a substituição
        ramo = Ramo(formulas=[beta_maior, beta_menor], expandidos=set())

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertEqual(formula, beta_menor)
        self.assertEqual(tipo, "beta_or")

    def test_desempate_beta_com_tamanhos_iguais_mantem_primeiro(self):
        # Se os tamanhos forem iguais (< estrito), mantém a primeira beta encontrada
        beta1 = FormulaMarcada(self.P | self.Q, True)  # beta_or (tamanho 3)
        beta2 = FormulaMarcada(self.R & self.S, False) # beta_and (tamanho 3)
        ramo = Ramo(formulas=[beta1, beta2], expandidos=set())

        formula, tipo = seletor.selecionar_formula(ramo)
        self.assertEqual(formula, beta1)
        self.assertEqual(tipo, "beta_or")


if __name__ == '__main__':
    unittest.main()
