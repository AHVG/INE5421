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
    
    def automate_union(self, automate):
        new_states = self.states.union(automate.states) 
        new_initial_state = "q0"
        new_final_states = self.final_states | automate.final_states
        new_alphabet = self.alphabet.union(automate.alphabet)
        new_transitions = self.transitions | automate.transitions | {('q0', '&') : {self.initial_state, automate.initial_state}}
        
        return NonDeterministicFiniteAutomaton(new_states, new_initial_state, new_final_states, new_alphabet, new_transitions)

    def __str__(self) -> str:
        def format_state(state):
            def format_set(s):
                """Formata conjuntos e frozensets para string sem a palavra 'frozenset', aplicando recursivamente."""
                if isinstance(s, (frozenset, set)):
                    return "{" + ",".join(sorted(format_set(e) for e in s)) + "}"
                return str(s)
            """Usa o método format_set para garantir a formatação correta."""
            return format_set(state)

        num_states = len(self.states)
        initial_state = format_state(self.initial_state)
        final_states = format_state(self.final_states)
        alphabet = "{" + ",".join(a for a in self.alphabet) + "}"
        transitions = ";".join(format_state(from_state) + "," + symbol + "," + format_state(to_state) for (from_state, symbol), to_state in self.transitions.items())

        return f"{num_states};{initial_state};{final_states};{alphabet};{transitions}"


class DeterministicFiniteAutomaton(FiniteAutomaton):

    def minimize(self):
        new_initial_state = self.initial_state
        new_alphabet = self.alphabet
        new_transitions = self.transitions.copy()

        # Constrói a partição inicial: estados finais e não finais
        partition = [self.final_states, set(self.states) - set(self.final_states)]

        def find_group(state, partition):
            """Encontra o grupo de uma partição ao qual o estado pertence."""
            for group in partition:
                if state in group:
                    return group
            return None

        while True:
            new_partition = []
            for group in partition:
                # Tenta dividir o grupo atual com base nas transições
                partitions = {}
                for state in group:
                    key = []
                    for symbol in new_alphabet:
                        next_state = self.transition(state, symbol)
                        if next_state:
                            key.append(frozenset(find_group(next_state, partition)))  # converte para frozenset
                        else:
                            key.append(None)
                    key = tuple(key)  # converte a lista para uma tupla
                    if key not in partitions:
                        partitions[key] = set()
                    partitions[key].add(state)
                
                new_partition.extend(partitions.values())
            
            if len(new_partition) == len(partition):
                break  # Nenhuma alteração na partição
            partition = new_partition

        # Mapeia os novos estados
        state_for_group = {}
        for group in partition:
            new_state = frozenset(group)  # usa frozenset para representar o novo estado
            for state in group:
                state_for_group[state] = new_state

        # Define novos estados, transições e estados finais
        new_states = set(state_for_group.values())
        new_transitions = {}
        for (state, symbol), next_state in self.transitions.items():
            new_transitions[(state_for_group[state], symbol)] = state_for_group[next_state]

        new_final_states = {state_for_group[state] for state in self.final_states}
        new_initial_state = state_for_group[self.initial_state]

        return DeterministicFiniteAutomaton(new_states, new_initial_state, new_final_states, new_alphabet, new_transitions)



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
                    closure = self.epsilon_closure(frozenset(next_states))
                    new_transitions[(frozenset(states), symbol)] = closure

                    if closure not in new_states:
                        new_states.append(closure)

        # Determinando os novos estados finais
        for new_state in new_states:
            if self.final_states & new_state:
                new_final_states.add(new_state)

        return DeterministicFiniteAutomaton(new_states, new_initial_state, frozenset(new_final_states), new_alphabet, new_transitions)


class Node:
    """Classe para representar um nó na árvore de expressão regular."""
    def __init__(self, value, left=None, right=None):
        self.value = value  # Operador ou operando
        self.left = left    # Subárvore à esquerda
        self.right = right  # Subárvore à direita

    def __str__(self):
        return self.value


class Regex:
    def __init__(self, regex):
        """Inicializa a regex e constrói a árvore da expressão regular."""
        self.regex = regex
        self.regex = self.insert_concatenation(self.regex)
        self.postfix = self.to_postfix(self.regex)
        self.tree = self.build_tree(self.postfix)

    def insert_concatenation(self, regex):
        """Insere operadores de concatenação explícitos ('.') na regex."""
        result = []
        operators = {'|', '*', ')'}
        for i in range(len(regex)):
            c1 = regex[i]
            result.append(c1)
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                if (c1 not in {'|', '(',} and
                    c2 not in {'|', '*', ')'}):
                    result.append('.')
        return ''.join(result)

    def to_postfix(self, regex):
        """Converte a regex da notação infixa para pós-fixa usando o algoritmo Shunting Yard."""
        precedence = {'*': 3, '.': 2, '|': 1}
        associativity = {'*': 'right', '.': 'right', '|': 'left'}
        output = []
        stack_char = []
        for char in regex:
            if char in {'a', 'b', '&'}:
                output.append(char)
            elif char == '(':
                stack_char.append(char)
            elif char == ')':
                while stack_char and stack_char[-1] != '(':
                    output.append(stack_char.pop())
                stack_char.pop()  # Remove '('
            elif char in precedence:
                while (stack_char and stack_char[-1] != '(' and
                    ((associativity[char] == 'left' and precedence[char] <= precedence[stack_char[-1]]) or
                        (associativity[char] == 'right' and precedence[char] < precedence[stack_char[-1]]))):
                    output.append(stack_char.pop())
                stack_char.append(char)
            else:
                raise ValueError(f"Caractere inválido na regex: {char}")
        while stack_char:
            if stack_char[-1] == '(' or stack_char[-1] == ')':
                raise ValueError("Parênteses não balanceados na regex.")
            output.append(stack_char.pop())
        return ''.join(output)

    def build_tree(self, postfix):
        """Constrói a árvore de expressão regular a partir da notação pós-fixa."""
        stack_char = []
        for char in postfix:
            if char in {'a', 'b', '&'}:
                stack_char.append(Node(char))
            elif char == '*':
                operand = stack_char.pop()
                stack_char.append(Node(char, left=operand))
            elif char in {'.', '|'}:
                right = stack_char.pop()
                left = stack_char.pop()
                stack_char.append(Node(char, left, right))
            else:
                raise ValueError(f"Caractere inválido na notação pós-fixa: {char}")
        if len(stack_char) != 1:
            raise ValueError("Erro na construção da árvore: pilha final não possui apenas a raiz.")
        return stack_char[0]

    def post_order(self, node):
        """Percorre a árvore em ordem pós-fixa e retorna uma lista dos valores."""
        if node is None:
            return []
        result = []
        result += self.post_order(node.left)
        result += self.post_order(node.right)
        result.append(node.value)
        return result

    def regex_to_post_order_string(self):
        """Retorna a expressão em pós-ordem como uma string."""
        traversal = self.post_order(self.tree)
        return ''.join(traversal)

    def __str__(self):
        """Retorna a expressão regular e sua representação em pós-ordem."""
        return f"{self.regex_to_post_order_string()}"

    def regex_original(self):
        """Retorna a regex original sem operadores de concatenação explícitos."""
        # Remover os pontos adicionados para concatenação
        result = []
        for char in self.regex:
            if char != '.':
                result.append(char)
        return ''.join(result)


class RegexProcessor:
    def __init__(self):
        self.stack_char = []
        self.stack_automate = []
        self.max_state_value = 0

    def format_set(self, s):
        """Formata conjuntos e frozensets para string sem a palavra 'frozenset'."""
        if isinstance(s, frozenset) or isinstance(s, set):
            return "{" + ",".join(sorted(s)) + "}"
        return str(s)

    def concatenate(self):
        b = self.stack_char.pop()
        a = self.stack_char.pop()
        result = f"({a}.{b})"
        self.stack_char.append(result)
        b_automate = self.stack_automate.pop()
        a_automate = self.stack_automate.pop()
        a_union_b_states = b_automate.states.union(a_automate.states)

        new_states = a_union_b_states
        new_initial_state = a_automate.initial_state
        new_final_state = {list(b_automate.final_states)[0]}
        new_alphabet = b_automate.alphabet.union(a_automate.alphabet)
        new_transitions = b_automate.transitions | a_automate.transitions | {(list(a_automate.final_states)[0], '&'): {b_automate.initial_state}}
        
        result = NonDeterministicFiniteAutomaton(new_states, new_initial_state, new_final_state, new_alphabet, new_transitions)
        self.stack_automate.append(result)

    def union(self):
        b = self.stack_char.pop()
        a = self.stack_char.pop()
        result = f"({a}|{b})"
        self.stack_char.append(result)
        b_automate = self.stack_automate.pop()
        a_automate = self.stack_automate.pop()
        a_union_b_states = b_automate.states.union(a_automate.states)

        new_states = a_union_b_states.union({str(self.max_state_value + 1), str(self.max_state_value + 2)})
        new_initial_state = str(self.max_state_value + 1)
        new_final_state = {str(self.max_state_value + 2)}
        new_alphabet = b_automate.alphabet.union(a_automate.alphabet)
        new_transitions = b_automate.transitions | a_automate.transitions | \
                                                     {(str(self.max_state_value + 1), '&') : {b_automate.initial_state, a_automate.initial_state}, \
                                                      (list(b_automate.final_states)[0], '&') : {str(self.max_state_value + 2)}, \
                                                      (list(a_automate.final_states)[0], '&') : {str(self.max_state_value + 2)}}
        self.max_state_value += 2
        result = NonDeterministicFiniteAutomaton(new_states, new_initial_state, new_final_state, new_alphabet, new_transitions)
        self.stack_automate.append(result)

    def kleene_star(self):
        a = self.stack_char.pop()
        result = f"{a}*"
        self.stack_char.append(result)
        a_automate = self.stack_automate.pop()
        new_states = a_automate.states.union({str(self.max_state_value + 1), str(self.max_state_value + 2)})
        new_initial_state = str(self.max_state_value + 1)
        new_final_state = {str(self.max_state_value + 2)}
        new_alphabet = a_automate.alphabet
        new_transitions = a_automate.transitions | {(str(self.max_state_value + 1), '&') : {a_automate.initial_state, str(self.max_state_value + 2)}, \
                                                    (list(a_automate.final_states)[0], '&') : {str(self.max_state_value + 2), a_automate.initial_state}}
        self.max_state_value += 2
        result = NonDeterministicFiniteAutomaton(new_states, new_initial_state, new_final_state, new_alphabet, new_transitions)
        self.stack_automate.append(result)


    def get_ndfa_from_regex(self, expression):
        for char in expression:
            if char == '.':  
                self.concatenate()
            elif char == '|':  
                self.union()
            elif char == '*': 
                self.kleene_star()
            else:
                automate = NonDeterministicFiniteAutomaton(
                    {str(self.max_state_value + 1), str(self.max_state_value + 2)},
                    str(self.max_state_value + 1),
                    {str(self.max_state_value + 2)},
                    {char},
                    {(str(self.max_state_value + 1), char): {str(self.max_state_value + 2)}}
                )
                self.max_state_value += 2
                self.stack_char.append(char)
                self.stack_automate.append(automate)

        return self.stack_automate.pop()



def format_set(s):
    """Formata conjuntos e frozensets para string, sem a palavra 'frozenset', aplicando recursivamente."""
    if isinstance(s, (frozenset, set)):
        return "{" + ",".join(sorted(format_set(e) for e in s)) + "}"
    return str(s)


def main():
    """
    Entrada:
    <(&|b)(ab)*(&|a)><&|b|a|bb*a>
    
    Saída:
    <3;{1,2,4,5};{{1,2,4,5},{3,5},{2,4,5}};{a,b};{1,2,4,5},a,{3,5};{1,2,4,5},b,{2,4,5};{3,5},b,{2,4,5};{2,4,5},a,{3,5}>
    ...
    """
    vpl_input = argv[1] # **Não remover essa linha**, ela é responsável por receber a string de entrada do VPL
    
    # Dividir a entrada em duas partes
    parts = vpl_input[1:-1].split("><")

    if len(parts) != 2:
        print("Entrada inválida. Deve conter duas expressões regulares separadas por '><'.")
        return

    # Atribuir as duas partes às variáveis input1 e input2
    input1 = parts[0]
    input2 = parts[1]
    regex1 = Regex(input1)
    regex2 = Regex(input2)
    processor = RegexProcessor()

    # Processar as expressões regulares para obter os NDFA
    result1_ndfa = processor.get_ndfa_from_regex(regex1.regex_to_post_order_string())
    result2_ndfa = processor.get_ndfa_from_regex(regex2.regex_to_post_order_string())

    # Determinizar os NDFA
    dfa_1 = result1_ndfa.determinize()
    dfa_2 = result2_ndfa.determinize()

    # Minimizar os DFA
    m_dfa_1 = dfa_1.minimize()
    m_dfa_2 = dfa_2.minimize()

    # Realizar a união dos DFA minimizados
    union = m_dfa_1.automate_union(m_dfa_2)

    print(m_dfa_1)
    print()
    print(m_dfa_2)
    print()
    print(union)


if __name__ == "__main__":
    main()
