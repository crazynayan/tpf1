import networkx as nx
from networkx import DiGraph
from models import Component, State
from commands import cmd


class SmartComponent(Component):
    WITHIN_PATH = 'CAN GO WITHIN PATH ON OPPOSITE'
    LOOP = 'LOOPS ON OPPOSITE'

    def __init__(self, component):
        super().__init__()
        self.command = component.command
        self.references = component.references
        self.operands = component.operands
        self.direction = False
        self.display = False    # Will be True for all conditional and only set_data components that are related
        self.tag = ''
        self.follow_path = list()

    @classmethod
    def from_component(cls, component, direction=None, display=None, tag=None, follow_path=None):
        model = cls(component)
        model.display = display if display is not None else model.display
        if model.is_conditional:
            model.direction = direction if direction is not None else model.direction
            model.tag = tag if tag is not None else model.tag
            model.follow_path = follow_path if follow_path is not None else model.follow_path
        return model


class OldAnalyze:
    def __init__(self, head, tail, blocks):
        self.exit_states = list()
        self.blocks = blocks
        self._smart_blocks = list()
        self._states = list()
        if head in self.blocks:
            state = State(head)
            state.tail = tail
            self.smart_search(head, self.blocks[head].components.list_values[0], state)
        self._replace = list()

    def smart_search(self, label, component, state, save=True):
        """
        Recursive function that builds path in self._paths
        :param label: The current block label. (Start label on first call)
        :param component: The current component. (First component of block on first call)
        :param state: A state object with path, known and assume. (Default object with head & tail init on first call)
        :param save: Optional parameter that specifies whether the label needs to be saved in the path.
        :return: updated state for function calls (BAS). For other types return None.
        """
        if save:
            state = state.copy(path=True)
            state.path.append(label)
        if label == state.path[-1]:
            if not state.is_same(self._states):
                self._states.append(state)
                print(f'F:{len(self._states)}')
            return
        if component.is_exit:
            next_label = next(iter(component.get_goes()), None)
            if next_label:
                return self._next_label(next_label, state)
            else:
                if not state.is_same(self.exit_states):
                    self.exit_states.append(state)
                    if len(self.exit_states) % 10 == 0:
                        print(f'E:{len(self.exit_states)}')
                return state if cmd.check(component.command, 'return') else None
        call = next(iter(component.get_calls()), None)
        if call:
            returned_state = self._next_label(call, state)
            state = returned_state if returned_state is not None else state
        if not component.is_set and not component.is_conditional:
            return self._next_component(label, component, state)
        operands = component.operands.list_values
        if component.is_set:
            math = cmd.check(component.command, 'math')
            source_value = None
            source = None
            if operands[0].bit:
                if isinstance(operands[0].bit['bits'], int):
                    target = operands[0].bit['byte']
                    source_value = operands[0].bit['bits']
                else:  # TODO remove the complication of a bit being a string by doing macro lookup in operand create
                    target = operands[0]
                    source_value = 0 if math == '&' else 1
                    math = ''
            elif len(operands) == 1:
                target = operands[0]
                math = ''
                source_value = 0
            else:
                target = operands[0]
                source = operands[1]
            if cmd.check(component.command, 'set_2'):
                # Ensure target is the one that is always being set
                target, source = source, target
            source_value = source.constant if source and source.constant is not None else source_value
            source = str(source)
            target = str(target)
            target_value = state.value_from_variable(target) if state.value_from_variable(target) else 0
            source_value = state.known[source] if source_value is None and source in state.known else source_value
            source_is_known = True if source_value is not None else False
            source_value = state.assume[source] if source_value is None and source in state.assume else source_value
            source_value = 0 if source_value is None else source_value
            try:
                source_value = eval(f"{target_value} {math} {source_value}") if math else source_value
            except NameError:
                pass
            state = state.copy(variable=True)
            if source_is_known and (target in state.known or not math):
                state.known[target] = source_value
                if target in state.assume:
                    del state.assume[target]
            else:
                state.assume[target] = source_value
                if target in state.known:
                    del state.known[target]
        # Component is conditional
        if not component.is_conditional:
            return self._next_component(label, component, state)
        if component.is_key_value:
            # User defined macros that are branching around
            # Fall down first
            data_returned = self._next_component(label, component, state)
            next_labels = list(set(component.get_goes()))
            next_data_returned = None
            for next_label in next_labels:
                next_data_returned = self._next_label(next_label, state)
            return data_returned or next_data_returned
        # Component is conditional but not key_value
        next_label = next(iter(component.get_goes()), None)
        if len(operands) == 1 or cmd.check(component.command, 'math'):
            operand = str(operands[0])
            if state.value_from_variable(operand) is not None:
                # Evaluate the condition of the component with the stored state in variables
                # If match then go to that branch otherwise fall down
                if eval(f'state.value_from_variable(operand) {cmd.get_operator(component.condition)}'):
                    return self._next_label(next_label, state)
                else:
                    return self._next_component(label, component, state)
            else:
                # Scenario where operand is not present in variables
                # Save the value for False condition and fall down
                state = state.copy(variable=True)
                operator = cmd.get_operator(component.condition, opposite=True)
                state.assume[operand] = self._operand_value_by_operator(operator)
                data_returned = self._next_component(label, component, state)
                # Reverse the condition and go to the label
                state = state.copy(variable=True)
                operator = cmd.get_operator(component.condition, opposite=False)
                state.assume[operand] = self._operand_value_by_operator(operator)
                next_data_returned = self._next_label(next_label, state)
                return data_returned or next_data_returned
        if len(operands) == 2:
            operand1_type = state.get_operand_type(operands[0])
            operand2_type = state.get_operand_type(operands[1])
            operand1_value = state.get_operand_value(operands[0])
            operand2_value = state.get_operand_value(operands[1])
            operand1 = str(operands[0])
            operand2 = str(operands[1])
            if (operand1_type == 'constant' and operand2_type == 'known') or \
               (operand1_type == 'known' and operand2_type == 'constant') or \
               (operand1_type == 'known' and operand2_type == 'known'):
                # Scenario where all operands are either constant or known
                # Evaluate the condition of the component with the stored state in variables
                # If match then go to that branch otherwise fall down
                if eval(f'operand1_value {cmd.get_operator(component.condition)} operand2_value'):
                    return self._next_label(next_label, state)
                else:
                    return self._next_component(label, component, state)
            else:
                state = state.copy(variable=True)
                if operand2_type == 'new' or (operand2_type == 'assume' and operand1_type != 'new'):
                    # Ensure 'new' and 'assume' types are in operand 1
                    operand1_type, operand2_type = operand2_type, operand1_type
                    operand1_value, operand2_value = operand1_value, operand2_value
                if operand2_type == 'new':
                    # Assume operand2 to be 0 when both the operands are new
                    state.assume[operand2] = 0
                # Save the value for False condition and fall down
                operator = cmd.get_operator(component.condition, opposite=True)
                state.assume[operand1] = self._operand_value_by_operator(operator, operand2_value)
                data_returned = self._next_component(label, component, state)
                # Save the value for True condition and go to the label
                state = state.copy(variable=True)
                operator = cmd.get_operator(component.condition, opposite=False)
                state.assume[operand1] = self._operand_value_by_operator(operator, operand2_value)
                next_data_returned = self._next_label(next_label, state)
                return data_returned or next_data_returned

    @staticmethod
    def _operand_value_by_operator(operator, data=None):
        if data is None:
            value_list = [0, 1, -1]
        else:
            if isinstance(data, int):
                value_list = [data, data + 1, data - 1]
            elif isinstance(data, str):
                data1 = chr(ord(data[0]) + 1) + data[1:]
                data2 = chr(ord(data[0]) - 1) + data[1:]
                value_list = [data, data1, data2]
            else:
                value_list = [data]
        for value in value_list:
            if data is None and eval(f'value {operator}'):
                return value
            if data is not None and eval(f'data {operator} value'):
                return value
        return None

    def _next_label(self, label, state):
        # Go through the label as long as it is not looping and not going inside the path
        # states = self._states.copy()
        # states.extend(self.exit_states)
        if state.traverse(self.exit_states, label):
            return self.smart_search(label, self.blocks[label].components.list_values[0], state)

    def _next_component(self, label, component, state):
        fall_down = component.fall_down
        if fall_down:
            return self.smart_search(fall_down, self.blocks[fall_down].components.list_values[0], state)
        else:
            # If it comes here then it is NOT a last component of the block
            components = self.blocks[label].components.list_values
            next_component = components[components.index(component) + 1]
            return self.smart_search(label, next_component, state, save=False)

    def get_count(self):
        return len(self._states)

    def get_all(self):
        return self._states

    def get_normal_state(self):
        normal_len, normal = self._get_max(self._states)
        return normal[0] if normal_len else None

    @staticmethod
    def _get_max(states):
        if not states:
            return 0, list()
        max_len = max([len(state.path) for state in states])
        max_states = [state for state in states if len(state.path) == max_len]
        return max_len, max_states

    def update(self, states=None, smart_blocks=None):
        self._states = states if states is not None else self._states
        self._smart_blocks = smart_blocks if smart_blocks is not None else self._smart_blocks


class Analyze:
    def __init__(self, nodes, root=None):
        if root is None:
            self.root_label = next((label for label in nodes.keys() if label[:2] == '$$'), None)
        else:
            self.root_label = root
        graph = DiGraph()
        # Add all the goes and falls edges
        for label, node in nodes.items():
            graph.add_node(label)
            for next_label in node.get_next():
                graph.add_edge(label, next_label)
        # Add returns to nodes
        call_nodes = [node for _, node in nodes.items() if node.get_call()]
        return_nodes = [node for _, node in nodes.items() if node.is_return]
        for call_node in call_nodes:
            return_node = next(return_node for return_node in return_nodes
                               if nx.has_path(graph, call_node.get_call(), return_node.label))
            call_node.set_return(return_node.label)
            return_node.set_return(call_node.fall_down)
        # Add goes edges to subroutine calls
        for call_node in call_nodes:
            graph.add_edge(call_node.label, call_node.get_call())
            return_node = nodes[next(iter(call_node.get_returns()))]
            if len(return_node.get_returns()) == 1:
                # Include subroutine to the main path if there is only one call
                graph.add_edge(return_node.label, call_node.fall_down)
                graph.remove_edge(call_node.label, call_node.fall_down)
        # Create a DAG (Directed Acyclic Graph) from the graph. (Remove cycles)
        dag = graph.copy()
        loop_edges = list()
        while not nx.is_directed_acyclic_graph(dag):
            cycle_edges = nx.find_cycle(dag, self.root_label)
            loop_edges.append(cycle_edges[-1])
            dag.remove_edge(*cycle_edges[-1])
        # Add loops to the nodes
        for loop_edge in loop_edges:
            nodes[loop_edge[0]].set_loop(loop_edge[1])
        # Reduce all the extra paths ('OR' paths) in the dag
        dag = nx.transitive_reduction(dag)
        # Save paths to all exit points
        exit_labels = [node.label for _, node in nodes.items() if node.is_program_exit]
        flows = dict()
        for exit_label in exit_labels:
            paths = list(nx.all_simple_paths(dag, self.root_label, exit_label))
            flows[exit_label] = [{'path': path} for path in paths]
        # Save graphs, nodes and paths
        self.dag = dag
        self.graph = graph
        self.nodes = nodes
        self.flows = flows

    def get_heads(self):
        # noinspection PyCallingNonCallable
        return [in_node for in_node, in_degree in self.graph.in_degree() if in_degree == 0]

    def get_tails(self):
        # noinspection PyCallingNonCallable
        return [out_node for out_node, out_degree in self.graph.out_degree() if out_degree == 0]

    def show(self, exit_label):
        for flow in self.flows[exit_label]:
            state = State(flow['path'])
            state.capture_set = True
            for label in flow['path']:
                state.label = label
                for component in self.nodes[label].components.list_values:
                    state = component.execute(state)
            flow['state'] = state
        # Print to Terminal
        print(f"{'*'*60} VALID PATH {'*'*60}")
        valid_flows = [flow for flow in self.flows[exit_label] if flow['state'].valid]
        for index, flow in enumerate(valid_flows):
            print(index+1, flow['path'])
        for index, flow in enumerate(valid_flows):
            print(index+1, flow['state'].condition)
        print(f"{'*'*59} INVALID PATH {'*'*59}")
        invalid_flows = [flow for flow in self.flows[exit_label] if not flow['state'].valid]
        for index, flow in enumerate(invalid_flows):
            print(index+1, flow['path'])
        for index, flow in enumerate(invalid_flows):
            print(index+1, flow['state'].condition)
        for index, flow in enumerate(valid_flows):
            print(f"{'*'*60} VALID {index+1:4} {'*'*60}")
            print('\n'.join(flow['state'].text))
            print(f"Required {flow['state'].condition}")
            print(f"Output   {flow['state'].known}")
        # for index, flow in enumerate(invalid_flows):
        #     print(f"{'*'*60} INVLD {index+1:4} {'*'*60}")
        #     print('\n'.join(flow['state'].text))
