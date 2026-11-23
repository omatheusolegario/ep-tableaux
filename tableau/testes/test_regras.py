import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

import unittest

from code_base import And, Implies, Not, Or, Variable, vars

from estruturas import FormulaMarcada 
import regras


class BaseTestRegras(unittest.TestCase):
    """Classe base contendo configurações comuns e métodos utilitários de asserção."""

    def setUp(self):
        self.P, self.Q, self.R, self.S = vars('P', 'Q', 'R', 'S')

    def assert_formula_marcada(
        self, obtida: FormulaMarcada, formula_esperada, marca_esperada: bool
    ):
        """Valida se o objeto FormulaMarcada possui a marca correta e a fórmula estruturalmente idêntica."""
        self.assertIsInstance(
            obtida,
            FormulaMarcada,
            f"Esperado FormulaMarcada, obtido {type(obtida).__name__}",
        )
        self.assertEqual(
            obtida.marca,
            marca_esperada,
            f"Marca incorreta: esperado {marca_esperada}, obtido {obtida.marca}",
        )
        self.assertTrue(
            obtida.formula.is_identical(formula_esperada),
            f"Fórmula incorreta: esperado '{formula_esperada}', obtido '{obtida.formula}'",
        )


class TestAuxiliaresRegras(BaseTestRegras):
    """Testes para a função auxiliar _getChildren."""

    def test_get_children_binaria(self):
        fm = FormulaMarcada(self.P & self.Q, True)
        filhos = regras._getChildren(fm)
        self.assertEqual(len(filhos), 2)
        self.assertTrue(filhos[0].is_identical(self.P))
        self.assertTrue(filhos[1].is_identical(self.Q))

    def test_get_children_unaria(self):
        fm = FormulaMarcada(~self.P, True)
        filhos = regras._getChildren(fm)
        self.assertEqual(len(filhos), 1)
        self.assertTrue(filhos[0].is_identical(self.P))


class TestRegrasAlpha(BaseTestRegras):
    """Testes para as expansões do tipo Alpha (geram um único ramo com as novas fórmulas)."""

    def test_alpha_and(self):
        # T(P ^ Q) -> [[T(P), T(Q)]]
        fm = FormulaMarcada(self.P & self.Q, True)
        res = regras.alpha_and(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[0][1], self.Q, True)

    def test_alpha_and_composta(self):
        # T((P v Q) ^ (R => S)) -> [[T(P v Q), T(R => S)]]
        f1 = self.P | self.Q
        f2 = self.R >> self.S
        fm = FormulaMarcada(And(f1, f2), True)
        res = regras.alpha_and(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], f1, True)
        self.assert_formula_marcada(res[0][1], f2, True)

    def test_alpha_or(self):
        # F(P v Q) -> [[F(P), F(Q)]]
        fm = FormulaMarcada(self.P | self.Q, False)
        res = regras.alpha_or(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[0][1], self.Q, False)

    def test_alpha_or_composta(self):
        # F(~P v (Q ^ R)) -> [[F(~P), F(Q ^ R)]]
        f1 = ~self.P
        f2 = self.Q & self.R
        fm = FormulaMarcada(Or(f1, f2), False)
        res = regras.alpha_or(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], f1, False)
        self.assert_formula_marcada(res[0][1], f2, False)

    def test_alpha_implies(self):
        # F(P => Q) -> [[T(P), F(Q)]]
        fm = FormulaMarcada(self.P >> self.Q, False)
        res = regras.alpha_implies(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[0][1], self.Q, False)

    def test_alpha_implies_composta(self):
        # F((P ^ Q) => (R v S)) -> [[T(P ^ Q), F(R v S)]]
        ant = self.P & self.Q
        conseq = self.R | self.S
        fm = FormulaMarcada(ant >> conseq, False)
        res = regras.alpha_implies(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 2)
        self.assert_formula_marcada(res[0][0], ant, True)
        self.assert_formula_marcada(res[0][1], conseq, False)

    def test_alpha_not(self):
        # T(~P) -> [[F(P)]]
        fm = FormulaMarcada(~self.P, True)
        res = regras.alpha_not(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1)
        self.assert_formula_marcada(res[0][0], self.P, False)

    def test_alpha_not_composta(self):
        # T(~(P => Q)) -> [[F(P => Q)]]
        sub = self.P >> self.Q
        fm = FormulaMarcada(~sub, True)
        res = regras.alpha_not(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1)
        self.assert_formula_marcada(res[0][0], sub, False)


class TestRegrasBeta(BaseTestRegras):
    """Testes para as expansões do tipo Beta (geram bifurcações em ramos independentes)."""

    def test_beta_and(self):
        # F(P ^ Q) -> [[F(P)], [F(Q)]]
        fm = FormulaMarcada(self.P & self.Q, False)
        res = regras.beta_and(fm)

        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(len(res[1]), 1)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[1][0], self.Q, False)

    def test_beta_or(self):
        # T(P v Q) -> [[T(P)], [T(Q)]]
        fm = FormulaMarcada(self.P | self.Q, True)
        res = regras.beta_or(fm)

        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(len(res[1]), 1)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[1][0], self.Q, True)

    def test_beta_implies(self):
        # T(P => Q) -> [[F(P)], [T(Q)]]
        fm = FormulaMarcada(self.P >> self.Q, True)
        res = regras.beta_implies(fm)

        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(len(res[1]), 1)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[1][0], self.Q, True)

    def test_beta_implies_composta(self):
        # T((P ^ Q) => (R v S)) -> [[F(P ^ Q)], [T(R v S)]]
        ant = self.P & self.Q
        conseq = self.R | self.S
        fm = FormulaMarcada(ant >> conseq, True)
        res = regras.beta_implies(fm)

        self.assertEqual(len(res), 2)
        self.assertEqual(len(res[0]), 1)
        self.assertEqual(len(res[1]), 1)
        self.assert_formula_marcada(res[0][0], ant, False)
        self.assert_formula_marcada(res[1][0], conseq, True)

    def test_beta_not(self):
        # F(~P) -> [[T(P)]]
        fm = FormulaMarcada(~self.P, False)
        res = regras.beta_not(fm)

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0]), 1)
        self.assert_formula_marcada(res[0][0], self.P, True)


class TestAplicarRegra(BaseTestRegras):
    """Testes para a função despachante aplicar_regra."""

    def test_aplicar_alpha_and(self):
        fm = FormulaMarcada(self.P & self.Q, True)
        res = regras.aplicar_regra((fm, "alpha_and"))
        self.assertEqual(len(res), 1)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[0][1], self.Q, True)

    def test_aplicar_beta_and(self):
        fm = FormulaMarcada(self.P & self.Q, False)
        res = regras.aplicar_regra((fm, "beta_and"))
        self.assertEqual(len(res), 2)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[1][0], self.Q, False)

    def test_aplicar_alpha_or(self):
        fm = FormulaMarcada(self.P | self.Q, False)
        res = regras.aplicar_regra((fm, "alpha_or"))
        self.assertEqual(len(res), 1)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[0][1], self.Q, False)

    def test_aplicar_beta_or(self):
        fm = FormulaMarcada(self.P | self.Q, True)
        res = regras.aplicar_regra((fm, "beta_or"))
        self.assertEqual(len(res), 2)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[1][0], self.Q, True)

    def test_aplicar_alpha_implies(self):
        fm = FormulaMarcada(self.P >> self.Q, False)
        res = regras.aplicar_regra((fm, "alpha_implies"))
        self.assertEqual(len(res), 1)
        self.assert_formula_marcada(res[0][0], self.P, True)
        self.assert_formula_marcada(res[0][1], self.Q, False)

    def test_aplicar_beta_implies(self):
        fm = FormulaMarcada(self.P >> self.Q, True)
        res = regras.aplicar_regra((fm, "beta_implies"))
        self.assertEqual(len(res), 2)
        self.assert_formula_marcada(res[0][0], self.P, False)
        self.assert_formula_marcada(res[1][0], self.Q, True)

    def test_aplicar_alpha_not(self):
        fm = FormulaMarcada(~self.P, True)
        res = regras.aplicar_regra((fm, "alpha_not"))
        self.assertEqual(len(res), 1)
        self.assert_formula_marcada(res[0][0], self.P, False)

    def test_aplicar_beta_not(self):
        fm = FormulaMarcada(~self.P, False)
        res = regras.aplicar_regra((fm, "beta_not"))
        self.assertEqual(len(res), 1)
        self.assert_formula_marcada(res[0][0], self.P, True)


if __name__ == '__main__':
    unittest.main()
