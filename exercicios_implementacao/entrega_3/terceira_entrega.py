from sys import argv
import re
import copy

class ContextFreeGrammar:
    def __init__(self, N, T, P, S):
        self.N = N  # Conjunto de variáveis (não-terminais)
        self.T = T  # Conjunto de terminais
        self.P = P  # Dicionário de produções onde a chave é o não-terminal e o valor é uma lista de produções
        self.S = S  # Símbolo inicial

        self.non_terminals_order = self.bfs_non_terminals()

    def __str__(self):
        # Formatar os conjuntos N, T e o símbolo inicial S
        N_str = "{" + ",".join(sorted(self.N)) + "}"
        T_str = "{" + ",".join(sorted(self.T)) + "}"
        S_str = "{" + self.S + "}"

        # Formatar as produções
        producoes = []
        for A in sorted(self.P.keys()):
            for prod in self.P[A]:
                if prod:
                    prod_str = "".join(prod)
                else:
                    prod_str = "&"
                producoes.append(f"{A} = {prod_str}")
        P_str = "; ".join(producoes)  # Junta as produções com "; "

        return f"{N_str}{T_str}{S_str}{{{P_str}}}"

    def identify_non_terminal_epsilon(self):
        E = set()
        while True:
            # Q := {X | X ∈ N e X não está em E e existe uma produção X ::= Y1Y2...Yn com Y1, Y2, ..., Yn ∈ E}
            Q = set()
            for X in self.N:
                if X not in E:
                    for prod in self.P.get(X, []):
                        if prod:
                            if all(Y in E for Y in prod[0]):
                                Q.add(X)
                        else:
                            Q.add(X)
            # Se Q for vazio, não há novos símbolos para adicionar
            if not Q:
                break
            E.update(Q)
        return E


    def eliminate_non_terminal_epsilon(self):
        # Identifica o conjunto E dos ε-não-terminais
        E = self.identify_non_terminal_epsilon()
        # Constrói P' sem as ε-produções
        P_prime = {A: [prod for prod in self.P.get(A, []) if prod != []] for A in self.P}
        # Adiciona produções alternativas removendo ε-não-terminais conforme necessário
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
        # Adiciona produções para o novo símbolo inicial, se necessário
        if self.S in E:
            S_prime = self.S + "'"  # Novo símbolo inicial S'
            P_prime[S_prime] = [[self.S], []]
            N_prime = self.N | {S_prime}
            self.non_terminals_order.append(S_prime)
        else:
            S_prime = self.S
            N_prime = self.N

        # Atualiza a gramática com os novos conjuntos de produções e não-terminais
        self.N = N_prime
        self.P = P_prime
        self.S = S_prime


        return copy.deepcopy(self)
    
    def eliminate_circular_productions(self):
        for non_terminal in self.P:
            # Filtra produções removendo aquelas que são do tipo A -> A
            self.P[non_terminal] = [
                prod for prod in self.P[non_terminal]
                if not (len(prod) == 1 and prod[0] == non_terminal)
            ]
        
        return copy.deepcopy(self)
    
    def eliminate_unit_productions(self):
        P_prime = {}  # Novo conjunto de produções

        # Construir NA para cada A ∈ N
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

        # Constrói P' sem as produções unitárias
        for A in self.N:
            P_prime[A] = []
            for B in N_A[A]:
                for prod in self.P.get(B, []):
                    if len(prod) != 1 or prod[0] not in self.N:
                        if prod not in P_prime[A]:
                            P_prime[A].append(prod)

        self.P = P_prime  # Atualiza P com o novo conjunto de produções P'
        self.eliminate_unreachable_symbols()

        return copy.deepcopy(self)

    def eliminate_unproductive_symbols(self):
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
            # print("L(G) = ∅")
            self.N = set()
            self.P = {}

        return copy.deepcopy(self)

    def eliminate_unreachable_symbols(self):
        # Elimina símbolos não-terminais inalcançáveis, a partir do bfs
        non_terminals = self.bfs_non_terminals()
        for non_teminal in list(self.N):
            if non_teminal not in non_terminals:
                self.N.remove(non_teminal)
                self.P.pop(non_teminal)

        return copy.deepcopy(self)

    def eliminate_direct_left_recursion(self, non_terminal):
        prods = self.P.get(non_terminal, [])
        alpha_prods = []  # A ::= Aα
        beta_prods = []   # A ::= β

        for prod in prods:
            if prod:
                tmp = prod[0]
                if len(tmp) > 0 and tmp[0] == non_terminal:
                    # Produção recursiva à esquerda
                    alpha_prods.append([tmp[1:]])  # Remove A do início da produção
                else:
                    # Produção não-recursiva à esquerda
                    beta_prods.append([tmp])

        if alpha_prods:
            # Cria um novo não-terminal para lidar com a recursão à esquerda
            new_non_terminal = non_terminal + "'"
            while new_non_terminal in self.N or new_non_terminal in self.T:
                new_non_terminal += "'"
            self.N.add(new_non_terminal)

            # Atualiza produções para A
            self.P[non_terminal] = []
            for beta in beta_prods:
                if beta:
                    self.P[non_terminal].append([beta[0] + new_non_terminal])
                else:
                    # Lida com epsilon em produções beta
                    self.P[non_terminal].append([new_non_terminal])

            # Produções para A'
            self.P[new_non_terminal] = []
            for alpha in alpha_prods:
                self.P[new_non_terminal].append([alpha[0] + new_non_terminal])
            # Adiciona epsilon produção para A'
            self.P[new_non_terminal].append([])
        else:
            # Sem recursão direta à esquerda
            self.P[non_terminal] = prods

    def bfs_non_terminals(self):
        # Função auxiliar para dividir uma produção em símbolos
        def split_production(production_str):
            pattern = r"[A-Z]'+|[A-Z]|[a-z]|\S"
            symbols = re.findall(pattern, production_str)
            return symbols

        visited = set()
        queue = [self.S]
        order = []
        # BFS para visitar todos os não-terminais
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                order.append(current)
                for prod in self.P.get(current, []):
                    if prod:
                        prod_str = ''.join(prod)
                        symbols = split_production(prod_str)
                        for symbol in symbols:
                            
                            if symbol in self.N and symbol not in visited:
                                queue.append(symbol)

        return order
        
    def eliminate_left_recursion(self):
        non_terminals = self.non_terminals_order
        for i in range(len(non_terminals)):
            Ai = non_terminals[i]
            for j in range(i):
                Aj = non_terminals[j]
                new_prods = []
                # Substitui Ai ::= Aj α por Ai ::= β α, onde Aj ::= β
                for prod in self.P.get(Ai, []):
                    if prod:
                        tmp = prod[0]
                        if len(tmp) > 0 and tmp[0] == Aj:
                            alpha = prod[0][1:]  # α
                            self.P[Ai].remove([tmp])  # Remove Ai ::= Aj α
                            for beta in self.P.get(Aj, []):
                                if beta:
                                    beta_ = beta[0]
                                    new_prod = beta_ + alpha  # β α
                                    new_prods.append([new_prod])
                self.P[Ai].extend(new_prods)
            # Elimina recursões diretas em Ai
            self.eliminate_direct_left_recursion(Ai)
        #self.eliminate_unreachable_symbols()
        
        return copy.deepcopy(self)

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
    result1 = cfg.eliminate_non_terminal_epsilon().eliminate_circular_productions().eliminate_unit_productions()
    result2 = cfg.eliminate_left_recursion()
    print(f"<<{result1}><{result2}>>")

if __name__ == '__main__':
    main()