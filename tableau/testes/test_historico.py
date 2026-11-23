import io
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from code_base import Variable, And, Or, vars
from estruturas import EstadoTableau, EventoHistorico, FormulaMarcada, Ramo
import historico

class TestFormulaMarcadaFormatacao(unittest.TestCase):
    """Testes para a função auxiliar _formula_marcada."""

    def setUp(self):
        self.P, self.Q = vars('P', 'Q')

    def test_formula_com_marca_true(self):
        fm = FormulaMarcada(self.P, True)
        self.assertEqual(historico._formula_marcada(fm), f"T({self.P})")

    def test_formula_com_marca_false(self):
        fm = FormulaMarcada(self.P & self.Q, False)
        self.assertEqual(historico._formula_marcada(fm), f"F({self.P & self.Q})")


class TestRegistrarEvento(unittest.TestCase):
    """Testes para a função registrar_evento."""

    def setUp(self):
        self.P, self.Q = vars('P', 'Q')
        self.ramo = Ramo(formulas=[], expandidos=set())
        self.estado = EstadoTableau(
            ramo_atual=self.ramo,
            ramos_pendentes=[],
            historico=[]
        )

    def test_expansao_sem_formula_lanca_excecao(self):
        with self.assertRaises(ValueError):
            historico.registrar_evento(
                self.estado,
                self.ramo,
                "expansao",
                formula=None,
                nome_regra="alpha_and"
            )

    def test_expansao_sem_nome_regra_lanca_excecao(self):
        fm = FormulaMarcada(self.P & self.Q, True)
        with self.assertRaises(ValueError):
            historico.registrar_evento(
                self.estado,
                self.ramo,
                "expansao",
                formula=fm,
                nome_regra=None
            )

    def test_registrar_expansao_sucesso(self):
        fm = FormulaMarcada(self.P & self.Q, True)
        f_p = FormulaMarcada(self.P, True)
        f_q = FormulaMarcada(self.Q, True)

        # Regra alpha gerando [T(P), T(Q)]
        geradas = [[f_p, f_q]]
        evento = historico.registrar_evento(
            self.estado,
            self.ramo,
            "expansao",
            formula=fm,
            nome_regra="alpha_and",
            expansao="alpha",
            geradas=geradas
        )

        self.assertIsInstance(evento, EventoHistorico)
        self.assertEqual(evento.id_ramo, self.ramo.id)
        self.assertEqual(evento.acao, "expansao")
        self.assertEqual(evento.id_formula, fm.id)
        self.assertEqual(evento.formula, f"T({self.P & self.Q})")
        self.assertEqual(evento.nome_regra, "alpha_and")
        self.assertEqual(evento.expansao, "alpha")
        self.assertEqual(evento.geradas, ((f"T({self.P})", f"T({self.Q})"),))
        self.assertIn(evento, self.estado.historico)
        self.assertEqual(len(self.estado.historico), 1)

    def test_registrar_evento_controle_sem_formula(self):
        evento = historico.registrar_evento(
            self.estado,
            self.ramo,
            "fechamento"
        )
        self.assertEqual(evento.acao, "fechamento")
        self.assertIsNone(evento.id_formula)
        self.assertIsNone(evento.formula)
        self.assertIsNone(evento.nome_regra)
        self.assertEqual(evento.geradas, ())
        self.assertEqual(len(self.estado.historico), 1)


class TestSequenciaRegras(unittest.TestCase):
    """Testes para a extração da sequência [(regra, fórmula), ...]."""

    def setUp(self):
        self.P, self.Q = vars('P', 'Q')

    def test_historico_vazio(self):
        self.assertEqual(historico.sequencia_regras([]), [])

    def test_ignora_eventos_de_controle(self):
        e1 = EventoHistorico(id_ramo=1, acao="inicio", id_formula=None, geradas=())
        e2 = EventoHistorico(id_ramo=1, acao="fechamento", id_formula=None, geradas=())
        resultado = historico.sequencia_regras([e1, e2])
        self.assertEqual(resultado, [])

    def test_extrai_apenas_expansoes_validas(self):
        e_exp1 = EventoHistorico(
            id_ramo=1,
            acao="expansao",
            id_formula=1,
            nome_regra="alpha_and",
            formula=f"T({self.P & self.Q})",
            geradas=()
        )
        e_controle = EventoHistorico(
            id_ramo=1,
            acao="bifurcacao",
            id_formula=None,
            geradas=()
        )
        e_exp2 = EventoHistorico(
            id_ramo=2,
            acao="expansao",
            id_formula=2,
            nome_regra="beta_or",
            formula=f"T({self.P | self.Q})",
            geradas=()
        )

        lista = [e_exp1, e_controle, e_exp2]
        esperado = [
            ("alpha_and", f"T({self.P & self.Q})"),
            ("beta_or", f"T({self.P | self.Q})")
        ]
        self.assertEqual(historico.sequencia_regras(lista), esperado)


class TestFormatarEImprimirHistorico(unittest.TestCase):
    """Testes para a formatação textual e exibição no terminal."""

    def setUp(self):
        self.P, self.Q = vars('P', 'Q')

    def test_formatar_historico_vazio(self):
        self.assertEqual(historico.formatar_historico([]), "Histórico vazio.")

    def test_formatar_historico_com_expansao_completa(self):
        evento = EventoHistorico(
            id_ramo=1,
            acao="expansao",
            id_formula=10,
            formula="T(P & Q)",
            nome_regra="alpha_and",
            expansao="alpha",
            geradas=(("T(P)", "T(Q)"),)
        )
        saida = historico.formatar_historico([evento])
        esperado = "1. Ramo 1: expansao | regra: alpha_and | tipo: alpha | fórmula #10: T(P & Q) | geradas: [T(P), T(Q)]"
        self.assertEqual(saida, esperado)

    def test_formatar_historico_com_multiplas_alternativas_beta(self):
        evento = EventoHistorico(
            id_ramo=2,
            acao="expansao",
            id_formula=11,
            formula="T(P | Q)",
            nome_regra="beta_or",
            expansao="beta",
            geradas=(("T(P)",), ("T(Q)",))
        )
        saida = historico.formatar_historico([evento])
        esperado = "1. Ramo 2: expansao | regra: beta_or | tipo: beta | fórmula #11: T(P | Q) | geradas: [T(P)] ou [T(Q)]"
        self.assertEqual(saida, esperado)

    def test_imprimir_historico_chama_print_corretamente(self):
        # geradas definido explicitamente como tupla vazia ()
        evento = EventoHistorico(
            id_ramo=1,
            acao="expansao",
            id_formula=5,
            formula="T(P & Q)",
            nome_regra="alpha_and",
            geradas=()
        )
        with patch('sys.stdout', new=io.StringIO()) as buffer_saida:
            historico.imprimir_historico([evento])
            conteudo = buffer_saida.getvalue()

        self.assertIn("1. Ramo 1: expansao | regra: alpha_and | fórmula #5: T(P & Q)", conteudo)
        self.assertIn("Sequência de regras: [('alpha_and', 'T(P & Q)')]", conteudo)


if __name__ == '__main__':
    unittest.main()
