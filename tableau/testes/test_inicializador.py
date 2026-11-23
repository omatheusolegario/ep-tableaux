import unittest

import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from code_base import ArgumentForm, vars
from estruturas import FormulaMarcada, Ramo
import inicializador

class TestInicializador(unittest.TestCase):
    """Testes unitários para a função iniciar(argument: ArgumentForm) do módulo inicializador."""

    def setUp(self):
        self.P, self.Q, self.R = vars('P', 'Q', 'R')

    def test_iniciar_retorna_tipo_ramo(self):
        # Valida se o retorno é uma instância de Ramo
        arg = ArgumentForm(self.P, conclusion=self.Q)
        ramo = inicializador.iniciar(arg)

        self.assertIsInstance(ramo, Ramo)
        self.assertIsInstance(ramo.formulas, list)
        self.assertIsInstance(ramo.expandidos, set)

    def test_iniciar_conjunto_expandidos_comeca_vazio(self):
        # O ramo inicial não deve ter nenhuma fórmula marcada como expandida
        arg = ArgumentForm(self.P, self.Q, conclusion=self.R)
        ramo = inicializador.iniciar(arg)

        self.assertEqual(ramo.expandidos, set())
        self.assertEqual(len(ramo.expandidos), 0)

    def test_iniciar_sem_premissas(self):
        # Sequente de tautologia: ⊢ P (nenhuma premissa, apenas conclusão False)
        arg = ArgumentForm(conclusion=self.P)
        ramo = inicializador.iniciar(arg)

        self.assertEqual(len(ramo.formulas), 1)

        formula_conclusao = ramo.formulas[0]
        self.assertIsInstance(formula_conclusao, FormulaMarcada)
        self.assertFalse(formula_conclusao.marca)
        self.assertTrue(formula_conclusao.formula.is_identical(self.P))

    def test_iniciar_com_uma_premissa(self):
        # Sequente: P ⊢ Q
        arg = ArgumentForm(self.P, conclusion=self.Q)
        ramo = inicializador.iniciar(arg)

        self.assertEqual(len(ramo.formulas), 2)

        # Premissa 1: T(P)
        f_prem = ramo.formulas[0]
        self.assertTrue(f_prem.marca)
        self.assertTrue(f_prem.formula.is_identical(self.P))

        # Conclusão: F(Q)
        f_conc = ramo.formulas[1]
        self.assertFalse(f_conc.marca)
        self.assertTrue(f_conc.formula.is_identical(self.Q))

    def test_iniciar_com_multiplas_premissas_e_ordem(self):
        # Sequente: P, Q ⊢ R
        premissas = [self.P, self.Q]
        arg = ArgumentForm(*premissas, conclusion=self.R)
        ramo = inicializador.iniciar(arg)

        self.assertEqual(len(ramo.formulas), 3)

        # Premissas marcadas com True mantendo a ordem
        self.assertTrue(ramo.formulas[0].marca)
        self.assertTrue(ramo.formulas[0].formula.is_identical(self.P))

        self.assertTrue(ramo.formulas[1].marca)
        self.assertTrue(ramo.formulas[1].formula.is_identical(self.Q))

        # Conclusão marcada com False
        self.assertFalse(ramo.formulas[2].marca)
        self.assertTrue(ramo.formulas[2].formula.is_identical(self.R))

    def test_iniciar_com_formulas_compostas(self):
        # Sequente: (P => Q), P ⊢ (P ^ Q)
        prem1 = self.P >> self.Q
        prem2 = self.P
        conc = self.P & self.Q

        arg = ArgumentForm(prem1, prem2, conclusion=conc)
        ramo = inicializador.iniciar(arg)

        self.assertEqual(len(ramo.formulas), 3)

        # Premissa 1: T(P => Q)
        self.assertTrue(ramo.formulas[0].marca)
        self.assertTrue(ramo.formulas[0].formula.is_identical(prem1))

        # Premissa 2: T(P)
        self.assertTrue(ramo.formulas[1].marca)
        self.assertTrue(ramo.formulas[1].formula.is_identical(prem2))

        # Conclusão: F(P ^ Q)
        self.assertFalse(ramo.formulas[2].marca)
        self.assertTrue(ramo.formulas[2].formula.is_identical(conc))


if __name__ == '__main__':
    unittest.main()
