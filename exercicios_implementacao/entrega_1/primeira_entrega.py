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

from sys import argv


class AF:

    def __init__(self, states, symbols, table, initial_state, final_states):
        self.states = states
        self.symbols = symbols
        self.table = table
        self.initial_state = initial_state
        self.final_states = final_states

    def transition(self, state, symbol):
        if state in self.table:
            transition = self.table[state]

            if symbol in transition:
                return transition[symbol]

        return None

    def empty_transition(self, state):
        states = [state]
        i = 0
        while len(states) > i:
            s = states[i]
            next_state = self.transition(s, "&")

            if next_state and next_state not in states:
                states.append(next_state)
            
            i += 1

        return states

    def determine(self):
        symbols = list(self.symbols)
        if "&" in symbols:
            symbols.remove("&")
        new_initial_state = tuple(self.empty_transition(self.initial_state))
        new_states = [new_initial_state]
        new_table = {}
        new_final_states = []

        i = 0
        while len(new_states) > i:
            states = new_states[i]
            new_table[states] = {}
            new_state = []

            for symbol in self.symbols:
                if symbol == "&":
                    continue

                for state in states:

                    aux = self.transition(state, symbol)

                    if aux:
                        if symbol in new_table[states]:
                            new_table[states][symbol].append(aux)
                        else:
                            new_table[states][symbol] = [aux]
                
                if symbol in new_table[states]:
                    new_table[states][symbol] = tuple(new_table[states][symbol])

                if symbol in new_table[states] and tuple(new_table[states][symbol]) not in new_states:
                    new_state.append(new_table[states][symbol])

            new_states.extend(new_state)
            i += 1
        
        for state in new_states:
            for final_state in self.final_states:
                if final_state in state:
                    new_final_states.append(state)
        
        new_final_states = tuple(new_final_states)

        return AF(new_states, symbols, new_table, new_initial_state, new_final_states)

    def __str__(self):
        # <<automato finito determinístico><automato finito determinístico mínimo>>
        # 3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}
        # 3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C
        # <número de estados>;<estado inicial>;{<estados finais>};{<alfabeto>};<transições>
        number_of_states = len(self.states)
        if isinstance(self.initial_state, tuple):
            initial_state = "{" + "".join(self.initial_state) + "}"
        else:
            initial_state = "{" + self.initial_state + "}"

        final_states = "{" + ",".join(["{" + "".join(f_s) + "}" for f_s in self.final_states]) + "}"
        alphabet = "{" + ",".join(self.symbols) + "}"
        transitions = []

        for state, value in self.table.items():
            for symbol, next_state in value.items():
                transitions.append(f"{'{' + ''.join(state) + '}'},{symbol},{'{' + ''.join(next_state) + '}'}")

        str_transitions = ";".join(transitions)
        return f"{number_of_states};{initial_state};{final_states};{alphabet};{str_transitions}"


def process_vpl_input(vpl_input):
    parts = vpl_input.split(';')
    num_states = int(parts[0])
    initial_state = parts[1]
    final_states = tuple(parts[2].strip('{}').split(','))
    alphabet = tuple(parts[3].strip('{}').split(','))

    states = list(initial_state)
    table = {}

    for transition in parts[4:]:
        state, symbol, next_state = transition.split(',')

        if state not in states:
            states.append(state)

        if next_state not in states:
            states.append(next_state)

        if state not in table:
            table[state] = {}

        table[state][symbol] = next_state

    return {
        'num_states': num_states,
        'states': states,
        'initial_state': initial_state,
        'final_states': final_states,
        'alphabet': alphabet,
        'transition_table': table
    }


def main():
    
    vpl_input = argv[1]
    infos = process_vpl_input(vpl_input)
    af = AF(infos["states"], infos["alphabet"], infos["transition_table"], infos["initial_state"], infos["final_states"])
    new_af = af.determine()
    print(af)


if __name__ == "__main__":
    main()