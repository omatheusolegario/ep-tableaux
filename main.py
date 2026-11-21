from code_base import ArgumentForm, vars
from tableau.motor import resolver

def main():
    # Logica para ler do terminal
    P, Q, R = vars('P', 'Q', 'R')

    arg_6 = ArgumentForm(
        (P >> Q) & (R >> Q),
        P | R,
        conclusion=Q
    )  
    resultado = resolver(arg_6)
    print(resultado)

if __name__ == "__main__":
    main()