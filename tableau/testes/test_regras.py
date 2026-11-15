import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from regras import *
from code_base import *

import unittest

class TestRegrasAlpha(unittest.TestCase):
	
	def setUp(self):
		self.P, self.Q, self.R, self.S = vars("P", "Q", "R", "S")
	
	def assert_estrutura(self, obtida: FormulaMarcada, esperada: FormulaMarcada, marca_esperada: bool):
		self.assertIsInstance(obtida, FormulaMarcada)
		self.assertEqual(obtida.marca, marca_esperada, "Marca incorreta")
		self.assertTrue(
			obtida.formula.is_identical(esperada),
			"Formula obtida incorreta")

	def test_alpha_and_atomos(self):
		fm = FormulaMarcada(self.P & self.Q, True)
		resultado = alpha_and(fm)
		
		self.assertEqual(len(resultado), 2)
		self.assert_estrutura(resultado[0], self.P, True)
		self.assert_estrutura(resultado[1], self.Q, True)


if __name__ == '__main__':
	unittest.main() 


