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


class FiniteAutomaton:
    def __init__(self, states, initial_state, final_states, alphabet, transitions) -> None:
        self.states = states
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.transitions = transitions

    def __str__(self) -> str:
        def format_state(state):
            return "{" + "".join(sorted(list(state))) + "}"

        num_states = len(self.states)
        initial_state = format_state(self.initial_state)
        final_states = "{" + ",".join(format_state(s) for s in self.final_states) + "}"
        alphabet = "{" + ",".join(a for a in self.alphabet) + "}"
        transitions = ";".join(format_state(from_state) + "," + symbol + "," + format_state(to_state) for (from_state, symbol), to_state in self.transitions.items())

        return f"{num_states};{initial_state};{final_states};{alphabet};{transitions}"


class DeterministicFiniteAutomaton(FiniteAutomaton):
    def minimize(self):
        pass

class NonDeterministicFiniteAutomaton(FiniteAutomaton):
    def transition(self, state, symbol):
        if (state, symbol) in self.transitions:
            return self.transitions[(state, symbol)]
        return None

    def epsilon_closure(self, state):
        if isinstance(state, frozenset):
            states = list(state)
        else:
            states = [state]

        i = 0
        while i < len(states):
            state = states[i]
            i += 1

            new_states = {}
            if (state, "&") in self.transitions:
                new_states = self.transitions[(state, "&")]

            for new_state in new_states:
                if new_state not in states:
                    states.append(new_state)

        return frozenset(states)

    def determinize(self):
        new_states = [self.epsilon_closure(self.initial_state)]
        new_initial_state = self.epsilon_closure(self.initial_state)
        new_final_states = set()

        new_alphabet = self.alphabet
        if "&" in new_alphabet:
            new_alphabet.remove("&")

        new_transitions = {}

        # Construindo as novas transições
        i = 0
        while i < len(new_states):
            states = new_states[i]
            i += 1
            for symbol in new_alphabet:
                next_states = set()
                for state in states:
                    next_state = self.transition(state, symbol)
                    if next_state:
                        next_states |= next_state

                if next_states:
                    new_transitions[(frozenset(states), symbol)] = self.epsilon_closure(frozenset(next_states))

                    if self.epsilon_closure(frozenset(next_states)) not in new_states:
                        new_states.append(self.epsilon_closure(frozenset(next_states)))

        # Determinando os novos estados finais
        for new_state in new_states:
            if self.final_states & new_state:
                new_final_states.add(new_state)

        return DeterministicFiniteAutomaton(new_states, new_initial_state, frozenset(new_final_states), new_alphabet, new_transitions)


def parse_automaton(automaton_str):
    parts = automaton_str.split(";")
    states = set()
    initial_state = parts[1]
    final_states = set(parts[2].strip('{}').split(","))
    alphabet = set(parts[3].strip('{}').split(","))

    transitions = {}
    for transition in parts[4:]:
        from_state, symbol, to_state = transition.split(",")
        if (from_state, symbol) not in transitions:
            transitions[(from_state, symbol)] = set()
        transitions[(from_state, symbol)].add(to_state)
        states.add(from_state)
        states.add(to_state)

    return states, initial_state, final_states, alphabet, transitions


def main():

    vpl_input = argv[1]
    states, initial_state, final_states, alphabet, transitions = parse_automaton(vpl_input)
    ndfa = NonDeterministicFiniteAutomaton(states, initial_state, final_states, alphabet, transitions)
    dfa = ndfa.determinize()
    test = "<5;{P};{{PQRS}};{0,1};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR};{PQR},0,{PQRS};{PQR},1,{PR};{PQRS},0,{PQRS};{PQRS},1,{PQRS};{PR},1,{P}>"
    print(f"<<{dfa}>{test}>")
    
    # 8;{P};{{PQS},{PRS},{PQRS},{PS}};{1,0};{P},1,{P};{P},0,{PQ};{PQ},1,{PR};{PQ},0,{PQR};{PR},1,{P};{PR},0,{PQS};{PQR},1,{PR};{PQR},0,{PQRS};{PQS},1,{PRS};{PQS},0,{PQRS};{PQRS},1,{PRS};{PQRS},0,{PQRS};{PRS},1,{PS};{PRS},0,{PQS};{PS},1,{PS};{PS},0,{PQS}
    # 8;{P};{{PQRS},{PQS},{PRS},{PS}};{0,1};{P},0,{PQ};{P},1,{P};{PQ},0,{PQR};{PQ},1,{PR};{PQR},0,{PQRS};{PQR},1,{PR};{PQRS},0,{PQRS};{PQRS},1,{PRS};{PQS},0,{PQRS};{PQS},1,{PRS};{PR},0,{PQS};{PR},1,{P};{PRS},0,{PQS};{PRS},1,{PS};{PS},0,{PQS};{PS},1,{PS}

if __name__ == "__main__":
    main()