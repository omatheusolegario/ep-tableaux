from code_base import ArgumentForm, vars, Proposition
from tableau.motor import resolver
from tableau.estruturas import ResultadoTableau

def _terminalToArgumentForm(entrada_premissa: str, entrada_conclusao: str) -> ArgumentForm:
    premissas = [premissa.strip() for premissa in entrada_premissa.split(",") if premissa.strip()]
    conclusao = entrada_conclusao.strip()

    if not conclusao:
        raise ValueError("A conclusão não pode ficar vazia.")
    
    proposicao = set()
    variaveis = [chr(i) for i in range(65, 91)]
    var_prop = dict()

    for premissa in premissas:
        for char in premissa:
            if char.isupper():
                if not {char}.issubset(proposicao):
                    proposicao.add(char)
                    variaveis[len(proposicao)-1], = vars(char)
                    var_prop[char]=variaveis[len(proposicao)-1]
            
    
    for char in conclusao:
        if char.isupper():
            if not {char}.issubset(proposicao):
                proposicao.add(char)
                variaveis[len(proposicao)-1], = vars(char)
                var_prop[char]=variaveis[len(proposicao)-1]

    escopo = {"__builtins__": None}

    premissas_obj = [eval(premissa, escopo, var_prop) for premissa in premissas]
    conclusao_obj = eval(conclusao, escopo, var_prop)    

    if not all(isinstance(premissa, Proposition) for premissa in premissas_obj) or not isinstance(conclusao_obj, Proposition):
         raise TypeError("As premissas e conclusão devem ser todos proposições válidas.")
    formula = ArgumentForm(*premissas_obj, conclusion= conclusao_obj)

    return formula

def exibir_resultado(resultado: ResultadoTableau):
    _bar()
    print(f"Válido: {'SIM' if resultado.valido else 'NÃO'}")

    if not resultado.valido:
        print(f"Contraexemplo: {resultado.contraexemplo}")

    regras_aplicadas= [
        (evento_hist.nome_regra, evento_hist.formula, evento_hist.geradas)
        for evento_hist in resultado.historico
        if evento_hist.acao == "expansao"
    ]

    print("\nSequência de regras aplicadas:")
    if regras_aplicadas:
        for i, (regra, formula, gerada) in enumerate(regras_aplicadas, start=1):
            if len(gerada)==1:
                geradas_formatada = ", ".join(gerada[0])
            else:
                geradas_formatada= " | ".join(f"({', '.join(ramo)})" for ramo in gerada)
            print(f"{i}. ({regra}, {formula} ==> {geradas_formatada })")
    else:
        print("Nenhuma regra aplicada.")
    
    _bar()

def _bar():
    print("\n=======================================================\n")

def cli():
    print("=======================================================")
    print("Provador por Tableaux Semânticos (Digite 0 para sair)")
    print("And: '&', Or: '|', Implies: '>>' e Not:'~'")
    print("=======================================================\n")
    while True:
        try:
            entrada_premissa = input("Digite as premissas (separadas por vírgulas, Enter se não houver):\n")
            if entrada_premissa == "0":
                _bar()
                break
            entrada_conclusao = input("Digite a conclusão:\n")
            if entrada_conclusao == "0":
                _bar()
                break
            
            sequente = _terminalToArgumentForm(entrada_premissa, entrada_conclusao)
            resultado = resolver(sequente)
             
        except Exception as erro:
             print(f"\nErro: {erro}")
             print("Tente inserir os dados novamente")
             continue

        exibir_resultado(resultado)
        
        opcao = input("Deseja tentar outra fórmula? (1 = sim, 0 = não): ").strip()
        while opcao not in ("0", "1"):
            opcao= input("Opção inválida. Digite 1 para sim 0 para não: ").strip()

        if opcao == "0":
            _bar()
            break

        _bar()