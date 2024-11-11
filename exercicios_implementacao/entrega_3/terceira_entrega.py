from sys import argv
import re

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
                    # Se algum caractere representar um terminal em E e a produção ter mais de um caractere
                    if char in E and len(prod[0]) > 1:
                        production = prod[0]
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

        return ContextFreeGrammar(self.N, self.T, self.P, self.S)
    
    def eliminate_circular_productions(self):
        for non_terminal in self.P:
            # Filtra produções removendo aquelas que são do tipo A -> A
            self.P[non_terminal] = [
                prod for prod in self.P[non_terminal]
                if not (len(prod) == 1 and prod[0] == non_terminal)
            ]
        
        return ContextFreeGrammar(self.N, self.T, self.P, self.S)
    
    def eliminate_unit_productions(self):
        P_prime = {}  # Novo conjunto de produções

        # Passo 1: Construir NA para cada A ∈ N
        N_A = {A: {A} for A in self.N}
        
        # Expande N_A para incluir todos os não-terminais alcançáveis por produções unitárias
        for A in self.N:
            queue = list(N_A[A])
            while queue:
                B = queue.pop(0)
                for prod in self.P.get(B, []):
                    if len(prod) == 1 and prod[0] in self.N:
                        C = prod[0]
                        if C not in N_A[A]:
                            N_A[A].add(C)
                            queue.append(C)

        # Passo 2: Construir P' sem as produções unitárias
        for A in self.N:
            P_prime[A] = []
            for B in N_A[A]:
                for prod in self.P.get(B, []):
                    if len(prod) != 1 or prod[0] not in self.N:
                        if prod not in P_prime[A]:
                            P_prime[A].append(prod)

        self.P = P_prime  # Atualiza P com o novo conjunto de produções P'

    def eliminate_unproductive_symbols(self):
        """Elimina símbolos improdutivos da gramática."""
        # Inicializa SP com os terminais e ε
        SP = set(self.T)

        # Repete até que nenhum novo símbolo seja adicionado a SP
        while True:
            # Encontra todos os não-terminais que têm pelo menos uma produção composta apenas por símbolos em SP
            Q = {
                X for X in self.N if X not in SP and any(
                    all(symbol in SP for symbol in prod) for prod in self.P.get(X, [])
                )
            }
            if not Q:
                break
            SP.update(Q)

        # Constrói N' e P' com símbolos produtivos
        N_prime = SP & self.N
        if self.S in SP:
            # Apenas mantém produções onde todos os símbolos são produtivos
            P_prime = {
                A: [prod for prod in self.P.get(A, []) if all(symbol in SP for symbol in prod)]
                for A in N_prime
            }
            # Remove entradas vazias de produções
            self.N = N_prime
            self.P = {A: prods for A, prods in P_prime.items() if prods}
        else:
            # Se o símbolo inicial não for produtivo, a linguagem é vazia
            print("L(G) = ∅")
            self.N = set()
            self.P = {}


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
    #cfg.eliminate_non_terminal_epsilon()
    #cfg.eliminate_circular_productions()
    #cfg.eliminate_unit_productions()
    cfg.eliminate_unproductive_symbols()
    print(cfg)


if __name__ == '__main__':
    main()