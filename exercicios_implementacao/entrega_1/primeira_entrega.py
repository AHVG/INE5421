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
        self.states: str = states
        self.symbols: set[str] = symbols
        self.table: dict[str, dict[str, set[str]]] = table
        self.initial_state: str = initial_state
        self.final_states: set[str] = final_states

    def transition(self, state: str, symbol: str) -> set[str] | None:
        if state in self.table:
            transition = self.table[state]

            if symbol in transition:
                return transition[symbol]

        return None

    def empty_transition(self, state: str) -> set[str]:
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
                    new_table[s][symbol] = next_state
                else:
                    new_table[s][symbol] = next_state

                for s in state:
                    if s in self.final_states:
                        final_states.add(state)
                        break

        return AF(new_table.keys(), symbols, new_table, initial_state, final_states)

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

    vpl_input = argv[1]
    infos = process_vpl_input(vpl_input)
    af = AF(infos["states"], infos["alphabet"], infos["transition_table"], infos["initial_state"], infos["final_states"])
    print(af.determine())



if __name__ == "__main__":
    main()