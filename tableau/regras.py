from .estruturas import FormulaMarcada

import sys
sys.path.insert(0, "../")

from code_base import *

def _getChildren(formula_marcada: FormulaMarcada):
	return [c for c in formula_marcada.formula.children]

def alpha_and(formula_marcada: FormulaMarcada) -> list[list[FormulaMarcada]]:
	"""Retorna o resultado da expansão do tipo Alpha And."""
	children =_getChildren(formula_marcada)	

	new_c1 = FormulaMarcada(children[0], True)
	new_c2 = FormulaMarcada(children[1], True)

	return [[new_c1, new_c2]]

def alpha_or(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]:
	"""Retorna o resultado da expansão do tipo Alpha Or."""
	children = _getChildren(formula_marcada)

	new_c1 = FormulaMarcada(children[0], False)
	new_c2 = FormulaMarcada(children[1], False)
	return [[new_c1, new_c2]]

def alpha_implies(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]: 
	"""Retorna o resultado da expansão do tipo Alpha Implies."""
	children = _getChildren(formula_marcada)      	
 
	new_c1 = FormulaMarcada(children[0], True) 
	new_c2 = FormulaMarcada(children[1], False)
	return [[new_c1, new_c2]]

def alpha_not(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]: 
	"""Retorna o resultado da expansão do tipo Alpha Not."""
	children = _getChildren(formula_marcada)

	new_c1 = FormulaMarcada(children[0], False)
	return [[new_c1]]

def beta_and(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]: 
	"""Retorna o resultado da expansão do tipo Beta And."""
	children = _getChildren(formula_marcada)
	
	ramo1 = FormulaMarcada(children[0], False)
	ramo2 = FormulaMarcada(children[1], False)

	return [[ramo1], [ramo2]]

def beta_or(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]:
	"""Retorna o resultado da expansão do tipo Beta Or."""
	children = _getChildren(formula_marcada)

	ramo1 = FormulaMarcada(children[0], True)
	ramo2 = FormulaMarcada(children[1], True)

	return [[ramo1], [ramo2]]

def beta_implies(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]:
	"""Retorna o resultado da expansão do tipo Beta Implies."""
	children = _getChildren(formula_marcada)

	ramo1 = FormulaMarcada(children[0], False)
	ramo2 = FormulaMarcada(children[1], True)
	
	return [[ramo1], [ramo2]]

def beta_not(formula_marcada: FormulaMarcada)-> list[list[FormulaMarcada]]:
	"""Retorna o resultado da expansão do tipo Beta Not."""
	children = _getChildren(formula_marcada)
	
	ramo1 = FormulaMarcada(children[0], True)

	return [[ramo1]]

def aplicar_regra(formula: tuple[FormulaMarcada | None, str | None]) -> list[list[FormulaMarcada]]:
	"""De acordo com a formula e seu tipo, retorna a expansão utilizando a regra correta."""
	formula_selecionada, tipo = formula
	match tipo:
		case "alpha_and":
			return alpha_and(formula_selecionada)
		case "beta_and":
			return beta_and(formula_selecionada)
		case "alpha_or":
			return alpha_or(formula_selecionada)
		case "beta_or":
			return beta_or(formula_selecionada)
		case "alpha_implies":
			return alpha_implies(formula_selecionada)
		case "beta_implies":
			return beta_implies(formula_selecionada)
		case "alpha_not":
			return alpha_not(formula_selecionada)
		case "beta_not":
			return beta_not(formula_selecionada)
