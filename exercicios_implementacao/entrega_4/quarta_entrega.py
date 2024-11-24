import sys
import re

def parse_input(vpl_input):
    """Parsa a entrada e retorna os componentes da gramática."""
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

def compute_first(N, T, P):
    """Calcula o conjunto First para cada não-terminal."""
    first = {non_terminal: set() for non_terminal in N}
    changed = True
    while changed:
        changed = False
        for A in N:
            for production in P.get(A, []):
                if production == ['&']:
                    if '&' not in first[A]:
                        first[A].add('&')
                        changed = True
                else:
                    for symbol_ in production:
                        if symbol_:
                            for symbol in symbol_:
                                if symbol in T:
                                    if symbol not in first[A]:
                                        first[A].add(symbol)
                                        changed = True
                                    break  # Não precisa continuar após encontrar um terminal
                                elif symbol in N:
                                    # Antes de atualizar, verificamos se há novos elementos para adicionar
                                    new_elements = first[symbol] - set('&')
                                    if not new_elements.issubset(first[A]):
                                        first[A].update(new_elements)
                                        changed = True
                                    if '&' in first[symbol]:
                                        # Continua para o próximo símbolo na produção
                                        continue
                                    else:
                                        break  # Não adiciona '&' e não continua
                                else:
                                    break
                            else:
                                break
                    else:
                        # Se percorrer toda a produção sem 'break', adiciona '&'
                        if '&' not in first[A]:
                            first[A].add('&')
                            changed = True
    return first

def compute_follow(N, T, P, S, first):
    """Calcula o conjunto Follow para cada não-terminal."""
    follow = {non_terminal: set() for non_terminal in N}
    follow[S].add('$')  # Adiciona o símbolo de fim de entrada ao Follow(S)
    changed = True
    while changed:
        changed = False
        for A in N:
            for production in P.get(A, []):
                production_str = ''.join(production)
                for idx in range(len(production_str)):
                    B = production_str[idx]
                    if B in N:
                        beta = production_str[idx+1:]
                        # Calcula First(beta)
                        first_beta = set()
                        if beta:
                            nullable = True
                            for symbol in beta:
                                if symbol in T:
                                    first_beta.add(symbol)
                                    nullable = False
                                    break
                                elif symbol in N:
                                    first_beta.update(first[symbol] - set('&'))
                                    if '&' in first[symbol]:
                                        continue
                                    else:
                                        nullable = False
                                        break
                                else:
                                    nullable = False
                                    break
                            if nullable:
                                first_beta.add('&')
                        else:
                            first_beta.add('&')
                        # Adiciona First(beta) - {&} ao Follow(B)
                        before = len(follow[B])
                        follow[B].update(first_beta - set('&'))
                        after = len(follow[B])
                        if after > before:
                            changed = True
                        # Se First(beta) contém &, adiciona Follow(A) ao Follow(B)
                        if '&' in first_beta:
                            before = len(follow[B])
                            follow[B].update(follow[A])
                            after = len(follow[B])
                            if after > before:
                                changed = True
        return follow

def format_output(N, first, follow):
    """Formata a saída conforme especificado."""
    output = []
    for non_terminal in N:
        first_set = ', '.join(sorted(first[non_terminal]))
        follow_set = ', '.join(sorted(follow[non_terminal]))
        output.append(f"First({non_terminal}) = {{{first_set}}}; Follow({non_terminal}) = {{{follow_set}}};")
    return ' '.join(output)

def main():
    vpl_input = sys.argv[1]  # **Não remover esta linha**, ela recebe a string de entrada do VPL
    N, T, P, S = parse_input(vpl_input)
    first = compute_first(N, T, P)
    follow = compute_follow(N, T, P, S, first)
    output = format_output(N, first, follow)
    print(output)

if __name__ == "__main__":
    main()