import networkx as nx
from networkx import DiGraph
from models import Component, Block, State, Node
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


class SmartBlock(Block):
    def __init__(self, block, prior_path, follow_path):
        super().__init__(block.label)
        components = list()
        # Get the true components that goes or falls down to any where in the path
        true_components = [component for component in block.components.list_values
                           if set(component.get_goes()) & set(follow_path)]
        for component in block.components.list_values:
            display = True if component.is_conditional else False
            if component in true_components:
                if component == true_components[-1] and block.fall_down not in follow_path:
                    # Last component that goes to the path. (Does NOT fall down to the path)
                    # No other components are added after this
                    components.append(SmartComponent.from_component(component,
                                                                    display=display,
                                                                    direction=True,
                                                                    follow_path=follow_path))
                    break
                else:
                    components.append(SmartComponent.from_component(component,
                                                                    display=display,
                                                                    tag=SmartComponent.WITHIN_PATH))
            elif set(component.get_goes()) & set(prior_path):
                components.append(SmartComponent.from_component(component, display=display, tag=SmartComponent.LOOP))
            elif follow_path or block.ends_in_program_exit():
                components.append(SmartComponent.from_component(component, display=display))
        self.components = components


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
        if label == state.tail:
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

    def create_smart_blocks(self, state=None):
        state = self.get_normal_state() if state is None else state
        if state is None:
            return list()
        smart_blocks = list()
        # Step 1 - Create a list SmartBlocks for each label in the path
        for index, label in enumerate(state.path):
            prior_path = state.path[: index + 1]
            follow_path = state.path[index + 1:] if label != state.path[-1] else list()
            smart_blocks.append(SmartBlock(self.blocks[label], prior_path, follow_path))
        # Step 2 - Reverse the path
        smart_blocks.reverse()
        for block in smart_blocks:
            block.components.reverse()
        # Step 3 - Update the display attribute of each component
        for main_block_index, block in enumerate(smart_blocks):
            for main_index, component in enumerate(block.components):
                if not component.is_conditional:
                    continue
                # Get the operands of the current component
                operands = [operand for operand in component.operands.list_values
                            if not operand.key_value and operand.constant is None]
                if component == block.components[-1]:
                    main_block_index += 1
                exit_flag = False
                for block_index in range(main_block_index, len(smart_blocks)):
                    start_index = main_index + 1 if smart_blocks[block_index].label == block.label else 0
                    for index in range(start_index, len(smart_blocks[block_index].components)):
                        display, operands = smart_blocks[block_index].components[index].check_set(operands)
                        if display:
                            smart_blocks[block_index].components[index].display = True
                            if not operands:
                                exit_flag = True
                                break
                    if exit_flag:
                        break
        # Step 4 - Restore the order of the path
        smart_blocks.reverse()
        for block in smart_blocks:
            block.components.reverse()
        return smart_blocks

    def get_smart_text(self, state=None):
        if state:
            smart_blocks = self.create_smart_blocks(state)
        elif self._smart_blocks:
            smart_blocks = self._smart_blocks
        else:
            smart_blocks = self.create_smart_blocks()
        text = list()
        for block in smart_blocks:
            text.append(block.label)
            block_text = [f"{' '*10}{component.get_text(component.direction, component.follow_path):40}{component.tag}"
                          for component in block.components
                          if component.display]
            if block_text:
                text.extend(block_text)
        return '\n'.join(text)

    def update(self, states=None, smart_blocks=None):
        self._states = states if states is not None else self._states
        self._smart_blocks = smart_blocks if smart_blocks is not None else self._smart_blocks

    def normalize(self, states=None):
        states = self._states if states is None else states
        max_len, max_states = self._get_max(states)
        if not max_len:
            return states
        other_states = list()
        for state in states:
            if len(state.path) == max_len:
                continue
            found = next((max_state.path for max_state in max_states if set(state.path).issubset(max_state.path)), None)
            if not found:
                other_states.append(state)
        max_states.extend(self.normalize(other_states))
        return max_states


class Analyze:
    def __init__(self, nodes, root=None):
        self.nodes = nodes
        if root is None:
            self.root_label = next((label for label in nodes.keys() if label[:2] == '$$'), None)
        else:
            self.root_label = root
        graph = DiGraph()
        for label, node in nodes.items():
            graph.add_node(label)
            for next_label in node.get_next():
                graph.add_edge(label, next_label)
        self.graph = graph

    def get_heads(self):
        # noinspection PyCallingNonCallable
        return [in_node for in_node, in_degree in self.graph.in_degree() if in_degree == 0]

    def get_tails(self):
        # noinspection PyCallingNonCallable
        return [out_node for out_node, out_degree in self.graph.out_degree() if out_degree == 0]

    def get_head_tails(self):
        """
        Match all heads and tails that are in the path
        :return: a dict with head as the key and a list of tails that are in its path
        """
        head_tails = dict()
        for head in self.get_heads():
            for tail in self.get_tails():
                if nx.has_path(self.graph, head, tail):
                    if head in head_tails:
                        head_tails[head].append(tail)
                    else:
                        head_tails[head] = [tail]
        return head_tails

    def combine_calls(self):
        nodes_with_calls = [node for _, node in self.nodes.items() if node.get_calls()]
        head_tails = self.get_head_tails()
        for node in nodes_with_calls:
            components = node.components.list_values
            label_index = 0
            current_label = node.label
            for index, component in enumerate(components):
                if current_label != node.label:
                    self.nodes[current_label].components.append(component)
                    self.nodes[node.label].components.remove(component)
                if not component.is_call:
                    continue
                if index < len(components) - 1:
                    label_index += 1
                    if '.' not in node.label:
                        return_label = f'{current_label}.{label_index}'
                    else:
                        return_label = f"{current_label.split('.', 1)[0]}.{label_index}"
                    self.nodes[return_label] = Node(return_label, node.name)
                    self.graph.add_node(return_label)
                else:
                    # Calls like BAS will always have fall down label if they are last component
                    return_label = node.fall_down
                call_label = str(component.operands.list_values[1])
                component.add_references(goes=call_label)
                self.graph.add_edge(current_label, call_label)
                for tail in head_tails[call_label]:
                    # TODO If a branch goes to a subroutine label then it won't be part of head
                    self.nodes[tail].components[-1].add_references(goes=return_label)
                    self.graph.add_edge(tail, return_label)
                current_label = return_label




