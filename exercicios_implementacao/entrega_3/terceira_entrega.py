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
        E = set()
        while True:
            # Q := {X | X ∈ N and X not in E and there exists a production X ::= Y1Y2...Yn with Y1, Y2, ..., Yn ∈ E}
            Q = set()
            for X in self.N:
                if X not in E:
                    for prod in self.P.get(X, []):
                        if prod == [] or all(Y in E for Y in prod[0]):
                            Q.add(X)
                            break
            # If Q is empty, no new symbols to add
            if not Q:
                break
            E.update(Q)
        return E


    def eliminate_non_terminal_epsilon(self):
        """Elimina produções ε seguindo o algoritmo especificado."""
        # Passo 1: Identificar o conjunto E dos ε-não-terminais
        E = self.identify_non_terminal_epsilon()
        print(E)
        # Passo 2: Construir P' sem as ε-produções
        P_prime = {A: [prod for prod in self.P.get(A, []) if prod != []] for A in self.P}
        # Passo 3: Adicionar produções alternativas removendo ε-não-terminais conforme necessário
        modified = True
        while modified:
            modified = False
            for A in list(P_prime.keys()):
                new_productions = []
                for prod in P_prime[A]:
                    tmp = prod[0]
                    # Para cada símbolo em `prod`, verificar se ele pertence a E
                    for i, symbol in enumerate(tmp):
                        if symbol in E:
                            # Cria uma nova produção com o símbolo removido
                            new_prod = [tmp[:i] + tmp[i+1:]]
                            # Adiciona a nova produção se ela não for vazia e não estiver na lista de produções
                            if new_prod != [''] and new_prod not in P_prime[A]:
                                new_productions.append(new_prod)
                                modified = True
                P_prime[A].extend(new_productions)

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
        # SP := T
        SP = set(self.T)
        # Repita
        while True:
            # Q := {X | X ∈ N e X não está em SP e existe pelo menos uma produção X ::= X1X2...Xn tal que X1, X2, ..., Xn ∈ SP}
            Q = set()
            for X in self.N:
                if X not in SP:
                    for prod in self.P.get(X, []):
                        if prod:
                            if all(symbol in SP for symbol in prod[0]):
                                Q.add(X)
                                break
            # Até Q = ∅
            if not Q:
                break
            SP.update(Q)
        # N' := SP ∩ N
        N_prime = SP & self.N
        if self.S in SP:
            # P' := {p | p ∈ P e todos os símbolos de p ∈ SP}
            P_prime = {}
            for A in N_prime:
                new_prods = []
                for prod in self.P.get(A, []):
                    if prod:
                        if all(symbol in SP for symbol in prod[0]):
                            new_prods.append(prod)
                if new_prods:
                    P_prime[A] = new_prods
            self.N = N_prime
            self.P = P_prime
        else:
            print("L(G) = ∅")
            self.N = set()
            self.P = {}

    def eliminate_unreachable_symbols(self):
        """Elimina símbolos inalcançáveis da gramática."""
        # SA := {S}
        SA = {self.S}
        # Repita
        while True:
            # M := {X | X ∈ N ∪ T e X não está em SA e existe produção Y ::= αXβ com Y ∈ SA}
            M = set()
            for Y in SA & self.N:
                for prod in self.P.get(Y, []):
                    if prod:
                        for symbol in prod[0]:
                            if symbol not in SA and (symbol in self.N or symbol in self.T):
                                M.add(symbol)
            # Até M = ∅
            if not M:
                break
            SA.update(M)
        # N' := SA ∩ N
        self.N = SA & self.N
        # T' := SA ∩ T
        self.T = SA & self.T
        # P' := {p | p ∈ P e todos os símbolos de p ∈ SA}
        P_prime = {}
        for A in self.N:
            new_prods = []
            for prod in self.P.get(A, []):
                try:
                    if all(symbol in SA for symbol in prod[0]):
                        new_prods.append(prod)
                except:
                    new_prods.append([])
            if new_prods:
                P_prime[A] = new_prods
        self.P = P_prime


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
    vpl_input = argv[1] # **Não remover essa linha**, ela é responsável por receber a string de entrada do VPL
    N,T,P,S = parse_input(vpl_input)
    cfg = ContextFreeGrammar(N,T,P,S)
    #print(cfg)
    cfg.eliminate_non_terminal_epsilon()
    cfg.eliminate_circular_productions()
    cfg.eliminate_unit_productions()
    cfg.eliminate_unreachable_symbols()
    print(cfg)


if __name__ == '__main__':
    main()