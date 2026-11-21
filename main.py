from code_base import ArgumentForm, vars
from tableau.motor import resolver

def main():
    # Logica para ler do terminal
    P,Q,R,S = vars('P', 'Q', 'R', 'S')
    argumento = ArgumentForm(
                P, P >> Q,    #premises
                 conclusion = Q
                )
    resultado = resolver(argumento)
    print(resultado)

if __name__ == "__main__":
    main()