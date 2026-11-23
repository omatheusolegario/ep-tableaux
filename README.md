# Provador de Teoremas por Tableaux Semânticos

Implementação em Python de um provador automático de teoremas para o Cálculo Proposicional baseado no método dos Tableaux Semânticos. O projeto avalia a validade de sequentes lógicos da forma A1, ..., An |- B, identificando se o argumento é válido, gerando um contraexemplo em caso de invalidade e exibindo o histórico com a sequência de regras aplicadas.

## Sistema utilizado
<img width="1050" height="234" alt="image" src="https://github.com/user-attachments/assets/1c886933-2059-4da6-b983-d4b29e5046d2" />

## Uso para clientes

Segue um conjunto de instruções para utilizar o nosso provador de teoremas. Para isso, há duas opções: **Via Código** e **Via CLI**.

### Via Código
1) Instancie os átomos:
```
# todos os átomos que serão utilizados nas fórmulas precisam ser declarados
from code_base import ArgumentForm, vars, Proposition
P,Q= vars('P', 'Q')
```
2) Declare os sequentes:
```
sequente = ArgumentForm(
  P, P >> Q,    #premises
  conclusion = Q
)
```
3) Obtenha o resultado!
```
from tableau.motor import resolver
from tableau.estruturas import ResultadoTableau
resultado: ResultadoTableau = resolver(sequente)
```

Veja `tableau/estruturas.py` para entender melhor a estrutura das classes.

### Via CLI
1) Execute o arquivo `main.py`

2) Coloque suas premissas e conclusões:
<img width="1196" height="410" alt="image" src="https://github.com/user-attachments/assets/96899206-9b39-4843-ac0c-9022e11e06c2" />

3) Veja o resultado!
<img width="1028" height="332" alt="image" src="https://github.com/user-attachments/assets/3fcf771d-fdeb-4409-a879-ef2ea62d08dc" />

## Testes para desenvolvedores

O projeto possui testes unitários desenvolvidos com o framework `unittest`. A execução deve ser realizada na pasta raiz do repositório. 

### Testando todos os módulos

Para testar todos os módulos, utilize o comando: 
`python3 -m unittest discover -s tableau/testes -v` ou `python3 -m unittest discover -s tableau/testes -v`

### Testando módulos separadamente

Para testar um módulo em específico (que está presente em `tableau/testes/`), utilize o comando:
`python3 -m unittest tableau/testes/test_modulo_desejado.py -v` ou `python -m unittest tableau/testes/test_modulo_desejado.py -v`


