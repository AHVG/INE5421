"""
========= INSTRUÇÕES =========
    - Todo o código deve estar contido no arquivo main.py
    - O arquivo main.py deve conter uma função main que será chamada pelo VPL,
      essa função deve conter uma linha de código que recebe a string de entrada do VPL.
      Um exemplo de como isso pode ser feito está no arquivo main.py fornecido.
    - Você pode criar funções fora da main se preferir, mas se certifique de que a main chama essas funções.
    - Caso você prefira fazer o exercício em uma IDE e quiser testar o código localmente,
        é só passar a string de entrada como argumento na hora de executar o código.
            Exemplo: python3 main.py "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"

Formato da saída:   <<automato finito determinístico><automato finito determinístico mínimo>>
                    <<3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}><3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}>>

DICA: O programa avalia somente o que está dentro das tags <>.
"""
import copy

from sys import argv


class AF:

    def __init__(self, states, symbols, table, initial_state, final_states):
        self.states = states
        self.symbols = symbols
        self.table: dict[str, dict[str]] = table
        self.initial_state: str = initial_state
        self.final_states = final_states

    def transition(self, state: str, symbol: str):
        if state in self.table:
            transition = self.table[state]

            if symbol in transition:
                return transition[symbol]

        return None

    def empty_transition(self, state: str):
        states = [state]
        stack_states = []

        if temp := self.transition(state, "&"):
            stack_states = list(temp)

        while len(stack_states):
            temp = stack_states.pop()
            next_states = self.empty_transition(temp)

            if not next_states:
                continue

            for next_state in next_states:
                if next_state not in states:
                    states.append(next_state)

        return set(states)

    def determine(self):
        symbols = self.symbols
        # Removendo a transição epislon, pois é uma maquina deterministica
        if "&" in symbols:
            symbols.remove("&")
        initial_state = self.initial_state
        table = {}
        states = [self.empty_transition(self.initial_state)]

        while len(states):
            state = tuple(sorted(list(states.pop())))

            # Se ja existir na tabela, não tem razão de computar novamente
            if state in table:
                continue

            # Adiciona na tabela
            table[state] = {}

            # Adiciona as transições
            for symbol in symbols:
                for s in state:
                    next_state = self.transition(s, symbol)
                    if next_state and symbol in table[state]:
                        table[state][symbol] = table[state][symbol] | next_state
                    elif next_state:
                        table[state][symbol] = next_state

            # Adiciona os próximos estados para análise
            for symbol in symbols:
                if symbol not in table[state]:
                    continue

                new_state = []
                for s in table[state][symbol]:
                    new_state.extend(sorted(list(self.empty_transition(s))))

                states.append(tuple(sorted(new_state)))

        # converte tupla de estados para uma string e determina os estados finais
        new_table = {}
        final_states = set()
        for state, value in table.items():
            for symbol, next_state in value.items():
                s = "".join(sorted(list(state)))
                if s not in new_table:
                    new_table[s] = {}
                    new_table[s][symbol] = "".join(sorted(list(next_state)))
                else:
                    new_table[s][symbol] = "".join(sorted(list(next_state)))

                for s in state:
                    if s in self.final_states:
                        final_states.add("".join(sorted(list(state))))
                        break

        return AF(set(new_table.keys()), symbols, new_table, initial_state, final_states)

    def minimize(self):
        # Remover estados inalcançaveis
        new_states = self.states.copy()
        new_symbols = self.symbols.copy()
        new_table = copy.deepcopy(self.table)
        new_initial_state = self.initial_state
        new_final_states = self.final_states.copy()

        reachable_states = [self.initial_state]
        i = -1
        while reachable_states:
            i += 1
            if len(reachable_states) < i + 1:
                break

            current_state = reachable_states[i]
            for symbol in self.symbols:
                next_state = self.transition(current_state, symbol)
                if next_state not in reachable_states:
                    reachable_states.append(next_state)

        unreachable_states = list(set(new_states) - set(reachable_states))

        for unreachable_state in unreachable_states:
            new_table.pop(unreachable_state)
            new_states.remove(unreachable_state)
            new_final_states.remove(unreachable_state)

        # remover estados mortos
        final_states = list(new_final_states)
        i = -1
        while final_states:
            i += 1
            if len(final_states) < i + 1:
                break

            final_state = final_states[i]

            for state, value in new_table.items():
                for _, next_state in value.items():
                    if next_state == final_state and state not in final_states:
                        final_states.append(state)

        dead_states = list(set(new_states) - set(final_states))
        for dead_state in dead_states:
            new_table.pop(dead_state)
            new_states.remove(dead_state)
            new_final_states.remove(dead_state)

        # Remover estados equivalentes
        final = list(new_final_states.copy())
        others = list(new_states - new_final_states)
        eq_class = [final[:], others[:]]

        changed = False
        while True:
            state_to_eq_class = {}
            for c in eq_class:
                for s in c:
                    state_to_eq_class[s] = []
                    for symbol in new_symbols:
                        state = self.transition(s, symbol)
                        
                        for i, target in enumerate(eq_class):
                            if state in target:
                                state_to_eq_class[s].append(i)
        
            # Dicionários para armazenar os grupos
            final_grupos = {}
            others_grupos = {}

            # Função auxiliar para agrupar termos com o mesmo índice
            def agrupar_termos(grupos, termo, indices):
                indice_tuple = tuple(indices)
                if indice_tuple not in grupos:
                    grupos[indice_tuple] = []
                grupos[indice_tuple].append(termo)
            
            # Percorrendo os termos e agrupando com base no conjunto inicial
            for termo, indices in state_to_eq_class.items():
                if termo in final:
                    agrupar_termos(final_grupos, termo, indices)
                elif termo in others:
                    agrupar_termos(others_grupos, termo, indices)

            new_eq_class = [*final_grupos.values(), *others_grupos.values()]

            if len(new_eq_class) == len(eq_class):
                break
            
            eq_class = new_eq_class[:]

        print(eq_class)
        
        temp_table = {}
        for states in eq_class:
            format_state = "".join(sorted(list(set(list("".join(states))))))
            print(states, format_state)
            temp_table[format_state] = {}
            for state in states:
                for symbol in new_symbols:
                    # TODO: AQUI TA O ERRO
                    next_state = self.transition(state, symbol)
                    print(state, symbol, next_state)
                    if symbol not in temp_table[format_state].keys():
                        temp_table[format_state][symbol] = []
                    
                    if next_state:
                        temp_table[format_state][symbol].append(next_state)
            
            for state, value in temp_table.items():        
                for symbol, next_state in value.items():
                    temp_table[state][symbol] = "".join(sorted(list(set(list("".join(next_state))))))

        new_states = temp_table.keys()
        temp_final_states = []
        temp_initial_state = ""
        for state in new_states:
            for f_state in new_final_states:
                if f_state in state:
                    temp_final_states.append(state)
        
        
        for e_class in eq_class:
            if new_initial_state in e_class:
                temp_initial_state = "".join(sorted(list(set(list("".join(e_class))))))

        return AF(new_states, new_symbols, temp_table, temp_initial_state, set(temp_final_states))



    def __str__(self):
        # <<automato finito determinístico><automato finito determinístico mínimo>>
        # 3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}
        # 3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C
        # <número de estados>;<estado inicial>;{<estados finais>};{<alfabeto>};<transições>
        number_of_states = len(self.states)
        initial_state = "{" + "".join(self.initial_state) + "}"
        final_states = "{" + ",".join(["{" + "".join(f_s) + "}" for f_s in self.final_states]) + "}"
        alphabet = "{" + ",".join(self.symbols) + "}"

        transitions = []
        for state, value in self.table.items():
            for symbol, next_state in value.items():
                temp_state = "{" + str(state) + "}"
                temp_next_state = "{" + "".join(next_state) + "}"
                transitions.append(f"{temp_state},{symbol},{temp_next_state}")
        transitions = ";".join(transitions)

        return f"{number_of_states};{initial_state};{final_states};{alphabet};{transitions}"


def process_vpl_input(vpl_input):
    parts = vpl_input.split(';')
    num_states = int(parts[0])
    initial_state = parts[1]
    final_states = set(parts[2].strip('{}').split(','))
    alphabet = set(parts[3].strip('{}').split(','))

    states = set(initial_state)
    table = {}

    for transition in parts[4:]:
        state, symbol, next_state = transition.split(',')

        if state not in states:
            states.add(state)

        if next_state not in states:
            states.add(next_state)

        if state not in table:
            table[state] = {}

        if symbol in table[state]:
            table[state][symbol].add(next_state)
        else:
            table[state][symbol] = set(next_state)

    return {
        'num_states': num_states,
        'states': states,
        'initial_state': initial_state,
        'final_states': final_states,
        'alphabet': alphabet,
        'transition_table': table
    }


def main():
    # Entrada:        3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C
    # Saída:          3;{A};{{ABC},{BC},{C}};{2,1,3};{ABC},2,{B};{ABC},1,{A};{ABC},3,{C};{C},3,{C};{BC},2,{B};{BC},3,{C}
    # Saída esperada: 

    # Entrada:        4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S
    # Saída:          8;{P};{{PQS},{PRS},{PS},{PQRS}};{1,0};{P},1,{P};{P},0,{QP};{PQ},1,{RP};{PQ},0,{RQP};{PQR},1,{RP};{PQR},0,{RQSP};{PQRS},1,{RSP};{PQRS},0,{SRQP};{PRS},1,{SP};{PRS},0,{SQP};{PQS},1,{RSP};{PQS},0,{RQSP};{PS},1,{SP};{PS},0,{SQP};{PR},1,{P};{PR},0,{SQP}
    # Saída esperada: 8;{P};{{PQRS},{PQS},{PRS},{PS}};{0,1};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR};{PQR},0,{PQRS};{PQR},1,{PR};{PQRS},0,{PQRS};{PQRS},1,{PRS};{PQS},0,{PQRS};{PQS},1,{PRS};{PR},0,{PQS};{PR},1,{P};{PRS},0,{PQS};{PRS},1,{PS};{PS},0,{PQS};{PS},1,{PS}
    # Saída:          5;{P};{{PQRS}};{0,1};{PQRS},0,{PQRS};{PQRS},1,{PRS};{PQR},0,{PQRS};{PQR},1,{PR};{PR},0,{PQS};{PR},1,{P};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR}
    # Saída esperada: 5;{P};{{PQRS}};{0,1};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR};{PQR},0,{PQRS};{PQR},1,{PR};{PQRS},0,{PQRS};{PQRS},1,{PQRS};{PR},0,{PQRS};{PR},1,{P}

    # {PQRS},1,{PRS};{PR},0,{PQS};
    # {PQRS},1,{PQRS};{PR},0,{PQRS};

    vpl_input = argv[1]
    infos = process_vpl_input(vpl_input)
    af = AF(infos["states"], infos["alphabet"], infos["transition_table"], infos["initial_state"], infos["final_states"])
    af = af.determine()
    print(af)
    af = af.minimize()
    print(af)


if __name__ == "__main__":
    main()