import sys
import re

class IOHandler:
    @staticmethod
    def parse_input(vpl_input):
        # Expressão regular para encontrar os quatro conjuntos no formato "{...}"
        sets = re.findall(r"\{(.*?)\}", vpl_input)
        N = sets[0].split(',')          # Não-terminais
        T = sets[1].split(',')          # Terminais
        S = sets[2]                     # Símbolo inicial
        productions_raw = sets[3].split(';')  # Produções

        # Processa as produções
        P = {}
        for prod in productions_raw:
            if '=' in prod:
                left, right = [s.strip() for s in prod.split('=')]
                if left not in P:
                    P[left] = []
                # Adiciona o lado direito como uma lista contendo a string inteira
                right_side = right.strip()
                if right_side == '&':
                    P[left].append(['&'])  
                else:
                    P[left].append([right_side])  
        return N, T, P, S
    
    @staticmethod
    def format_output(N, first, follow):
        first_output = []
        follow_output = []
        for non_terminal in N:
            first_set = ', '.join(sorted(first[non_terminal]))
            follow_set = ', '.join(sorted(follow[non_terminal]))
            first_output.append(f"First({non_terminal}) = {{{first_set}}}")
            follow_output.append(f"Follow({non_terminal}) = {{{follow_set}}}")
        output = '; '.join(first_output + follow_output)
        return output

class ContextFreeGrammar:
    def __init__(self, N, T, P, S):
        self.N = N  # Conjunto de não-terminais
        self.T = T  # Conjunto de terminais
        self.P = P  # Produções
        self.S = S  # Símbolo inicial

    def compute_first(self):
        first = {symbol: set() for symbol in self.N}  # Inicializa FIRST para cada não-terminal
        for terminal in self.T:
            first[terminal] = {terminal}  # FIRST de um terminal é ele mesmo
        
        changed = True
        while changed:
            changed = False
            for X in self.N:
                for production_ in self.P[X]:
                    if production_:
                        production = production_[0]
                        if production == '&':  # Regra para epsilon
                            if '&' not in first[X]:
                                first[X].add('&')
                                changed = True
                        else:
                            symbol_ = ""
                            for symbol in production:
                                symbol_ += symbol
                                if symbol_ in self.T or symbol_ in self.N:
                                    before = len(first[X])
                                    first[X].update(first[symbol_] - {'&'})  # Adiciona FIRST do símbolo
                                    if '&' not in first[symbol_]:
                                        break  # Interrompe se não há epsilon
                                    if symbol_ == production[-1]:
                                        first[X].add('&')  # Adiciona epsilon se necessário
                                    after = len(first[X])
                                    if after > before:
                                        changed = True
                                    symbol_ = ""
        return first

    def compute_follow(self):
        follow = {A: set() for A in self.N}  # Inicializa FOLLOW para cada não-terminal
        follow[self.S].add('$')  # Adiciona $ ao FOLLOW do símbolo inicial
        first = self.compute_first()  # Calcula FIRST para auxiliar

        changed = True
        while changed:
            changed = False
            for A in self.N:
                for production_ in self.P[A]:
                    if production_:
                        production = production_[0]
                        for i, B in enumerate(production):
                            if B in self.N:
                                beta = production[i+1:]
                                if beta:
                                    # Se beta não é vazio
                                    first_beta = set()
                                    symbol_ = ""
                                    for symbol in beta:
                                        symbol_ += symbol
                                        if symbol_ in self.T or symbol_ in self.N:
                                            first_beta.update(first[symbol_] - {'&'})
                                            if '&' not in first[symbol_]:
                                                break
                                            symbol_ = ""
                                    else:
                                        last_beta = ""
                                        for i in range(1, len(beta) + 1):
                                            last_beta = beta[-i:]
                                            if last_beta in first.keys():
                                                print(last_beta, self.T, self.N)
                                                break
                                        if '&' in first[last_beta]:
                                            first_beta.add('&')
                                    before = len(follow[B])
                                    follow[B].update(first_beta - {'&'})  # Atualiza FOLLOW(B)
                                    after = len(follow[B])
                                    if after > before:
                                        changed = True
                                    # Se FIRST(beta) contém epsilon
                                    all_nullable = True
                                    symbol_ = ""  
                                    for symbol in beta:
                                        symbol_ += symbol
                                        if symbol_ in first.keys():
                                            if '&' not in first[symbol_]:
                                                all_nullable = False  
                                                break
                                            symbol_ = "" 
                                    # Se FIRST(beta) contém epsilon
                                    if all_nullable:
                                        before = len(follow[B])
                                        follow[B].update(follow[A])  
                                        after = len(follow[B])
                                        if after > before:
                                            changed = True
                                else:
                                    # Beta é vazio
                                    before = len(follow[B])
                                    follow[B].update(follow[A])  # Adiciona FOLLOW(A) a FOLLOW(B)
                                    after = len(follow[B])
                                    if after > before:
                                        changed = True
        return follow

def main():
    vpl_input = sys.argv[1]  # **Não remover esta linha**, ela recebe a string de entrada do VPL
    N, T, P, S = IOHandler.parse_input(vpl_input)  # Parsing da entrada
    cfg = ContextFreeGrammar(N, T, P, S)  
    first = cfg.compute_first()  # Computa o conjunto FIRST
    follow = cfg.compute_follow()  # Computa o conjunto FOLLOW
    output = IOHandler.format_output(N, first, follow)  # Formata a saída
    print(output)  # Imprime o resultado

if __name__ == "__main__":
    main()