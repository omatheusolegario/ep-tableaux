import sys
sys.path.insert(0, "../")
sys.path.insert(1, "../../")

from regras import *
from code_base import *

import unittest

class TestRegrasAlpha(unittest.TestCase):
	
	def setUp(self):
		self.P, self.Q, self.R, self.S = vars("P", "Q", "R", "S")
	
	def assertEstrutura(self, obtida: FormulaMarcada, esperada: FormulaMarcada, marca_esperada: bool):
		self.assertIsInstance(obtida, FormulaMarcada)
		self.assertEqual(obtida.marca, marca_esperada, "Marca incorreta")
		self.assertTrue(
			obtida.formula.is_identical(esperada),
			"Formula obtida incorreta")

	def test_alpha_and_atomos(self):
		fm = FormulaMarcada(self.P & self.Q, True)
		resultado = alpha_and(fm)
		
		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], self.P, True)
		self.assertEstrutura(resultado[1], self.Q, True)

	def test_alpha_and_composta(self):
		f1 = self.P >> self.Q
		f2 = self.R | self.S
		fm = FormulaMarcada(f1&f2, True)
		resultado = alpha_and(fm)		
	
		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], f1, True)
		self.assertEstrutura(resultado[1], f2, True) 

	def test_alpha_or_atomos(self):
		fm = FormulaMarcada(self.P|self.Q, False)
		resultado = alpha_or(fm)
		
		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], self.P, False)
		self.assertEstrutura(resultado[1], self.Q, False)

	def test_alpha_or_composta(self):
		f1 = self.P >> self.Q
		f2 = self.R & self.S
		fm = FormulaMarcada(f1|f2, False)
		resultado = alpha_or(fm)	
	
		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], f1, False)
		self.assertEstrutura(resultado[1], f2, False) 

	def test_alpha_implies_atomos(self):
		fm = FormulaMarcada(self.P >> self.Q, False)
		resultado = alpha_implies(fm)
	
		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], self.P, True)
		self.assertEstrutura(resultado[1], self.Q, False)

	def test_alpha_implies_composta(self):
		f1 = self.P >> self.Q
		f2 = self.R | self.S
		fm = FormulaMarcada(f1 >> f2, False)
		resultado = alpha_implies(fm)

		self.assertEqual(len(resultado), 2)
		self.assertEstrutura(resultado[0], f1, True)
		self.assertEstrutura(resultado[1], f2, False)
		
	def test_alpha_not_atomos(self):
		fm = FormulaMarcada(~self.P, True)
		resultado = alpha_not(fm)
	
		self.assertEqual(len(resultado), 1)
		self.assertEstrutura(resultado[0], self.P, False)

	def test_alpha_not_composta(self):
		f1 = self.P >> self.Q
		fm = FormulaMarcada(~f1, True)
		resultado = alpha_not(fm)		
	
		self.assertEqual(len(resultado), 1)
		self.assertEstrutura(resultado[0], f1, False)

if __name__ == '__main__':
	unittest.main() 


