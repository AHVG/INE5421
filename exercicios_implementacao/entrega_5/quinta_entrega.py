import sys
import re

class IOHandler:
    @staticmethod
    def parse_input(vpl_input):
        grammar_input, input_sentence = vpl_input.split('}; ')
        grammar_input += '}'    
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
        return N, T, P, S, input_sentence
    
    @staticmethod
    def format_output(N, S, T, parsing_table, is_ll1):
        table_entries = []
        for nt in N:
            for terminal in T + ['$']:
                if (nt, terminal) in parsing_table:
                    production = parsing_table[(nt, terminal)]
                    production_str = ''.join(production) if production != ['&'] else '&'
                    table_entries.append(f"[{nt},{terminal},{production_str}]")
        N_str = '{' + ','.join(N) + '}'
        T_str = '{' + ','.join(T + ['$']) + '}'
        output = f"<<{N_str};{S};{T_str};{''.join(table_entries)}><{'sim' if is_ll1 else 'não'}>>"
        return output

class ContextFreeGrammar:
    def __init__(self, N, T, P, S):
        self.N = N  # Conjunto de não-terminais
        self.T = T  # Conjunto de terminais
        self.P = P  # Produções
        self.S = S  # Símbolo inicial

    def is_LL1(self):
        no_left_recursion = self.check_left_recursion()
        is_left_factored = self.check_left_factoring()
        first_follow_disjoint = self.check_first_follow_disjoint()
        return no_left_recursion and is_left_factored and first_follow_disjoint

    def check_left_recursion(self):
        for A in self.N:
            for production_ in self.P.get(A, []):
                if production_:
                    production = production_[0]
                    if production and production[0] == A:
                        return False  # Recursão à esquerda encontrada
        return True

    def check_left_factoring(self):
        for A in self.N:
            prefixes = {}
            for production_ in self.P.get(A, []):
                if production_:
                    first_symbol = ""
                    for symbol in production_[0]:
                        first_symbol += symbol
                        if symbol in self.T or symbol in self.N:
                            break
                    if first_symbol in prefixes:
                        return False  # Necessita fatoração
                    prefixes[first_symbol] = True
        return True

    def check_first_follow_disjoint(self):
        first = self.compute_first()
        follow = self.compute_follow()
        for A in self.N:
            if '&' in first[A]:
                if first[A].intersection(follow[A]):
                    return False  # First(A) e Follow(A) não são disjuntos
        return True

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

    def compute_parsing_table(self):
        parsing_table = {}
        first = self.compute_first()
        follow = self.compute_follow()
        for A in self.N:
            for production in self.P[A]:
                if production == ['&']:
                    for b in follow[A]:
                        key = (A, b)
                        parsing_table[key] = production
                else:
                    first_set = set()
                    production_ = production[0]
                    if production_:
                        symbol_ = ""
                        for symbol in production_:
                            symbol_ += symbol
                            if symbol_ in self.T or symbol_ in self.N:
                                first_set.update(first[symbol_])
                                if '&' not in first[symbol_]:
                                    break
                                symbol_ = ""
                        else:
                            first_set.add('&')
                        for terminal in first_set - {'&'}:
                            key = (A, terminal)
                            parsing_table[key] = production_
                        if '&' in first_set:
                            for b in follow[A]:
                                key = (A, b)
                                parsing_table[key] = production_
        return parsing_table

def main():
    vpl_input = sys.argv[1]  # **Não remover esta linha**, ela recebe a string de entrada do VPL
    N, T, P, S, input_sentence = IOHandler.parse_input(vpl_input)  # Parsing da entrada
    cfg = ContextFreeGrammar(N, T, P, S)
    if not cfg.is_LL1():
        print("A gramática não é LL1.")
        return  
    parsing_table = cfg.compute_parsing_table()
    # word_is_valid = verify_word()
    word_is_valid = True 
    output = IOHandler.format_output(N, S, T, parsing_table, word_is_valid)
    print(output)  # Imprime o resultado

if __name__ == "__main__":
    main()