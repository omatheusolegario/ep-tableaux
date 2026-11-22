from code_base import ArgumentForm, vars, Proposition
from tableau.motor import resolver

def terminalToArgumentForm(entrada_premissa: str, entrada_conclusao: str) -> ArgumentForm:
    premissas = [premissa.strip() for premissa in entrada_premissa.split(",")]
    conclusao = entrada_conclusao.strip()
    proposicao = set()
    variaveis = [chr(i) for i in range(65, 91)]
    var_prop = dict()

    for premissa in premissas:
        for char in premissa:
            if char.isupper():
                if not {char}.issubset(proposicao):
                    proposicao.add(char)
                    variaveis[len(proposicao)] = vars(char)
                    var_prop[char]=variaveis[len(proposicao)]
            
    
    for char in conclusao:
            if not {char}.issubset(proposicao):
                proposicao.add(char)
                variaveis[len(proposicao)] = vars(char)
                var_prop[char]=variaveis[len(proposicao)]

    escopo = {"__builtins__": None}

    premissas_obj = [eval(premissa, escopo, var_prop) for premissa in premissas]
    conclusao_obj = eval(conclusao, escopo, var_prop)    

    if not all(isinstance(premissa, Proposition) for premissa in premissas) or not isinstance(conclusao, Proposition):
         raise TypeError("As premissas e conclusão devem ser todos proposições válidas.")
    formula = ArgumentForm(*premissas_obj, conclusion= conclusao_obj)

    return formula

def cli():
    print("===================================\n")
    while True:
        try:
            entrada_premissa = input("Digite as premissas (separadas por vírgulas):\n")
            entrada_conclusao = input("Digite a conclusão:\n")
             
            sequente = terminalToArgumentForm(entrada_premissa, entrada_conclusao)
            resultado = resolver(sequente)
             
        except Exception as erro:
             print(f"\nErro: {erro}")
             print("Tente inserir os dados novamente")
             continue

        print(resultado)
        opcao = input("\nDeseja tentar outra fórmula? (1 = sim, 0 = não): ")
        if opcao == "0":
            break
    