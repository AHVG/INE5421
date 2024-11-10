from sys import argv
import re
from itertools import chain, combinations

class ContextFreeGrammar:
    def __init__(self, N, T, P, S):
        self.N = N  # Conjunto de variáveis (não-terminais)
        self.T = T  # Conjunto de terminais
        self.P = P  # Dicionário de produções onde a chave é o não-terminal e o valor é uma lista de produções
        self.S = S  # Símbolo inicial

    def __str__(self):
        return f"{self.N}; {self.T}; {self.S}; {self.P}"


    def identify_non_terminal_epsilon(self):
        E = set()  # Conjunto de ε-não-terminais
        Q = {non_terminal for non_terminal in self.N if any(prod == [] for prod in self.P.get(non_terminal, []))}
        
        while Q:
            # Atualiza Q com não-terminais que têm uma produção composta apenas por elementos de E
            Q = {
                X for X in self.N if X not in E and any((all(Y in E for Y in char) for char in prod) for prod in self.P.get(X, []))
            }
            E.update(Q)  # Adiciona elementos de Q ao conjunto E
            
        return E


    def eliminate_non_terminal_epsilon(self):
        """Elimina produções ε seguindo o algoritmo especificado."""
        # Passo 1: Identificar o conjunto E dos ε-não-terminais
        E = self.identify_non_terminal_epsilon()
        # Passo 2: Construir P' sem as ε-produções
        P_prime = {A: [prod for prod in self.P.get(A, []) if prod != []] for A in self.P}

        # Passo 3: Adicionar produções alternativas removendo ε-não-terminais conforme necessário
        modified = True
        while modified:
            modified = False
            for A in list(P_prime.keys()):
                new_productions = []
                for prod in P_prime[A]:
                    # Para cada símbolo em `prod`, verificar se ele pertence a E
                    for i, symbol in enumerate(prod):
                        if symbol in E:
                            # Cria uma nova produção com o símbolo removido
                            new_prod = prod[:i] + prod[i+1:]
                            if new_prod and new_prod not in P_prime[A]:
                                new_productions.append(new_prod)
                                modified = True
                P_prime[A].extend(new_productions)

        P_prime_tmp = P_prime
        for non_terminal, prods in P_prime_tmp.items():
            for prod in prods:
                for char in prod[0]:
                    production = prod[0]
                    # Se algum caractere representar um terminal em E e a produção ter mais de um caractere
                    if char in E and len(production) > 1:
                        # Adiciona produção removendo variável anulável
                        P_prime[non_terminal].append([production.replace(char, "")])

        # Passo 4: Adicionar produções para o novo símbolo inicial, se necessário
        if self.S in E:
            S_prime = self.S + "'"  # Novo símbolo inicial S'
            P_prime[S_prime] = [[self.S], []]
            N_prime = self.N | {S_prime}
        else:
            S_prime = self.S
            N_prime = self.N

        # Atualiza a gramática com os novos conjuntos de produções e não-terminais
        self.N = N_prime
        self.P = P_prime
        self.S = S_prime

def parse_input(entrada):
    # Expressão regular para encontrar os quatro conjuntos no formato "{...}"
    conjuntos = re.findall(r"\{(.*?)\}", entrada)
    N = set(conjuntos[0].split(','))  
    T = set(conjuntos[1].split(','))  
    S = conjuntos[2]                 
    producoes_raw = conjuntos[3].split(';')  # Produções separadas por ponto e vírgula

    # Processando as produções para criar o dicionário de produções P
    P = {}
    for prod in producoes_raw:
        esquerda, direita = map(str.strip, prod.split('='))
        if esquerda not in P:
            P[esquerda] = []
        # Cada produção à direita é separada por espaços para formar a lista de símbolos
        P[esquerda].append([simbolo for simbolo in direita.split() if simbolo != '&'])

    return N, T, P, S


def main():
    N,T,P,S = parse_input(argv[1])
    cfg = ContextFreeGrammar(N,T,P,S)
    #print(cfg)
    cfg.eliminate_non_terminal_epsilon()
    print(cfg)


if __name__ == '__main__':
    main()