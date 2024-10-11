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

    def transition(self, state, symbol):
        return self.transitions.get((state, symbol), None)

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
        new_initial_state = self.initial_state
        new_final_states = set()
        new_alphabet = self.alphabet
        new_transitions = self.transitions.copy()

        # Remover estados inalcancaveis
        reachable_states = set()
        new_states = {self.initial_state}

        while new_states:
            state = new_states.pop()
            reachable_states.add(state)

            for symbol in self.alphabet:
                next_state = self.transition(state, symbol)
                if next_state and next_state not in reachable_states:
                    new_states.add(next_state)

        new_states = reachable_states
        new_transitions = {k: v for k, v in self.transitions.items() if k[0] in reachable_states}
        new_final_states = {state for state in self.final_states if state in reachable_states}

        # Remover estados mortos
        alive_states = set(new_final_states)
        changed = True

        while changed:
            changed = False
            for (state, symbol), next_state in new_transitions.items():
                if next_state in alive_states and state not in alive_states:
                    alive_states.add(state)
                    changed = True

        new_states = alive_states
        new_transitions = {(state, symbol): next_state for (state, symbol), next_state in new_transitions.items() if state in alive_states and next_state in alive_states}
        new_final_states = {state for state in new_final_states if state in alive_states}

        # Remover estados equivalentes
        partition = [new_final_states, new_states - new_final_states]

        while True:
            new_partition = []
            for group in partition:
                partitions = {}
                for state in group:
                    key = list({new_transitions.get((state, symbol), None) for symbol in new_alphabet})

                    for l, k in enumerate(key):
                        for j, p in enumerate(partition):
                            if k in p:
                                key[l] = j

                    key = tuple(key)

                    if key not in partitions:
                        partitions[key] = set()
                    partitions[key].add(state)

                new_partition.extend(partitions.values())

            if len(new_partition) == len(partition):
                break

            partition = new_partition
        

        new_partition = [group for group in partition if group]
        
        state_for_group = {}
        for group in new_partition:
            temp = frozenset(set.union(*[set(s) for s in group]))
            for state in group:
                state_for_group[state] = temp

        for group in new_partition:
            if new_initial_state in group:
                new_initial_state = frozenset(set.union(*[set(s) for s in group]))
                break
        new_new_transition = {}
        new_new_states = set()
        
        for group in new_partition:
            new_state = frozenset(set.union(*[set(s) for s in group]))
            for symbol in new_alphabet:
                for state in group:
                    next_state = new_transitions.get((state, symbol), None)
                    if next_state:
                        if (new_state, symbol) not in new_new_transition:
                            new_new_transition[(new_state, symbol)] = set()
    
                        if next_state in state_for_group:
                            new_new_transition[(new_state, symbol)].add(state_for_group[next_state])
                        else:
                            new_new_transition[(new_state, symbol)].add(next_state)

                if (new_state, symbol) in new_new_transition:
                    new_new_transition[(new_state, symbol)] = frozenset(set.union(*[set(s) for s in new_new_transition[(new_state, symbol)]]))
            new_new_states.add(new_state)

        new_states = new_new_states
        new_new_final_states = set()
        for f in new_states:
            for final_state in new_final_states:
                if final_state <= f:
                    new_new_final_states.add(f)
        new_final_states = new_new_final_states
        new_transitions = new_new_transition.copy()

        return DeterministicFiniteAutomaton(frozenset(new_states), new_initial_state, frozenset(new_final_states), new_alphabet, new_transitions)

class NonDeterministicFiniteAutomaton(FiniteAutomaton):
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
    print(states)
    print(initial_state)
    print(final_states)
    print(alphabet)
    print(transitions)
    dfa = ndfa.determinize()
    m_dfa = dfa.minimize()
    print(f"<<{dfa}>><<{m_dfa}>>")

    # Input: "6;S;{S,X};{a,b,c};S,a,A;S,b,A;S,b,C;S,c,C;A,a,M;A,b,B;A,b,X;A,c,D;A,c,X;B,a,A;B,b,A;B,b,C;B,c,C;C,a,E;C,a,X;C,b,B;c,b,X;C,c,M;D,a,A;D,b,A;D,b,C;D,c,M;E,a,M;E,b,A;E,b,C;E,c,C"
    # meu
    # {DMX},c,{M};{EMX},c,{C};{EMX},a,{M};{C},c,{M};{A},a,{M}>>
    # dele
    # {EMX},c,{C}>>


if __name__ == "__main__":
    main()

#  Output: <<11;{S};{DMX,BX,EX,EMX,DX,S};{a,b,c};{S},a,{A};{S},b,{AC};{S},c,{C};{A},a,{M};{A},b,{BX};{A},c,{DX};{AC},a,{EMX};{AC},b,{BX};{AC},c,{DMX};{C},a,{EX};{C},b,{B};{C},c,{M};{BX},a,{A};{BX},b,{AC};{BX},c,{C};{DX},a,{A};{DX},b,{AC};{DX},c,{M};{EMX},a,{M};{EMX},b,{AC};{EMX},c,{C};{DMX},a,{A};{DMX},b,{AC};{DMX},c,{M};{EX},a,{M};{EX},b,{AC};{EX},c,{C};{B},a,{A};{B},b,{AC};{B},c,{C}>>
# DMX BX EX EMX DX S

# Output: 7;{S};{{DMX},{BSX},{EMX}};{a,b,c};{DMX},a,{A};{DMX},b,{AC};{EMX},b,{AC};{EMX},c,{C};{BSX},a,{A};{BSX},b,{AC};{BSX},c,{C};{B},a,{A};{B},b,{AC};{B},c,{C};{C},a,{EMX};{C},b,{B};{AC},a,{EMX};{AC},b,{BSX};{AC},c,{DMX};{A},b,{BSX};{A},c,{DMX}
# DMX, BSX, EMX, A, AC, C, B


# "6;S;{S,X};{a,b,c};S,a,A;S,b,A;S,b,C;S,c,C;A,a,M;A,b,B;A,b,X;A,c,D;A,c,X;B,a,A;B,b,A;B,b,C;B,c,C;C,a,E;C,a,X;C,b,B;c,b,X;C,c,M;D,a,A;D,b,A;D,b,C;D,c,M;E,a,M;E,b,A;E,b,C;E,c,C"
#  Expected: 7;{BX};{{BX},{DMX},{EMX}};{a,b,c};{A},b,{BX};{A},c,{DMX};{AC},a,{EMX};{AC},b,{BX};{AC},c,{DMX};{B},a,{A};{B},b,{AC};{B},c,{C};{BX},a,{A};{BX},b,{AC};{BX},c,{C};{C},a,{EMX};{C},b,{B};{DMX},a,{A};{DMX},b,{AC};{EMX},b,{AC};{EMX},c,{C}
# BX, DMX, EMX, A, AC, B, C