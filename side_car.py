from itertools import product, combinations
from models import Block
from commands import cmd


class SmartComponent:
    def __init__(self, component):
        self._component = component
        self.direction = False

    def __repr__(self):
        return f'{self._component}({self.direction})'

    def __eq__(self, other):
        """
        Checks the equality of command and operands.
        Does NOT check for References.
        Key Value components (Executable Macros) are always considered unequal.
        Used in ComponentPath._check_valid_path to identify duplicate or unique components.
        :param other: Another SmartComponent object
        :return: True if equal else False
        """
        if not isinstance(other, type(self)):
            return False
        if self._component.is_key_value:
            return False
        if self._component.command != other._component.command:
            return False
        my_operands = self._component.operands.list_values
        other_operands = other._component.operands.list_values
        if len(my_operands) != len(other_operands):
            return False
        for index, operand in enumerate(my_operands):
            if operand != other_operands[index]:
                return False
        return True

    @property
    def conditional(self):
        return self._component.conditional

    @property
    def is_key_value(self):
        return self._component.is_key_value

    @property
    def condition(self):
        ref = next((ref for ref in self._component.references.list_values if ref.type == 'goes'), None)
        return ref.condition if ref else None

    @property
    def opposite_condition(self):
        return cmd.check(self.condition, 'opposite')

    def goes_to(self, lookup_label):
        found = next((label for label in self._component.get_goes() if label == lookup_label), None)
        return True if found else False

    def get_text(self, labels):
        return self._component.get_text(self.direction, labels)


class SmartBlock:
    def __init__(self, label):
        self._components = list()
        self.label = label
        self.next_label = None

    def __repr__(self):
        return f'{self.label}({len(self._components)})'

    def append(self, component):
        """
        Add a component to the list
        :param component: This needs to be an object of type Component
        :return: None
        """
        self._components.append(SmartComponent(component))

    def get(self):
        """
        Return a list of component
        :return: A list of component
        """
        return [component.get() for component in self._components]

    def get_conditional(self):
        """
        Return a list of smart component that have conditions.
        Useful for printing conditional text.
        :return: A list of smart component.
        """
        return [component for component in self._components if component.conditional]

    def update_direction(self, label):
        """
        Update the direction to True for the last component if it is going to the next label
        :param label: The label of the next item where this path leads to.
        :return: None
        """
        if self._components and self._components[-1].goes_to(label):
            self._components[-1].direction = True

    def get_text(self):
        text = list()
        text.append(f'{self.label}:')
        for component in self.get_conditional():
            text.append(f"{' '*10}{component.get_text([self.next_label])}")
        return '\n'.join(text)


class ComponentPath:
    NOT_IN_DUPLICATES = -1

    def __init__(self, path):
        self.path = path  # instance of Path object
        self.component_path = list()  # different combination of the list of components in the path
        self.valid_path = list()

    @property
    def is_valid(self):
        return True if self.valid_path else False

    def analyze(self, blocks=None):
        if not blocks:
            blocks = dict()
            for label in self.path.path:
                block = Block.query_first(name=self.path.name, label=label)
                if block:
                    blocks[label] = block
        component_paths = list()
        for index, label in enumerate(self.path.path):
            if label == self.path.path[-1]:
                break
            component_paths.append(blocks[label].get_path(self.path.path[index + 1]))
        # Component path is a list of paths
        # Each item in the list is a tuple of path
        # Each item in the tuple contains a component dictionary
        # Each component dictionary contains a 'label' and a list of 'items'
        # Each item in the list is a component
        component_path = list(product(*component_paths))
        # Create a new component path which is a 2 dimension list with each item as Smart Block object.
        # Each row shows a series of Smart Block path
        # Multiple rows indicate multiple path
        new_component_path = list()
        for path in component_path:
            new_path = list()
            for index, component_dict in enumerate(path):
                block = SmartBlock(component_dict['label'])
                for component in component_dict['items']:
                    block.append(component)
                # Set the direction of smart_components
                if component_dict != path[-1]:
                    block.next_label = path[index + 1]['label']
                else:
                    block.next_label = self.path.path[-1]
                block.update_direction(block.next_label)
                new_path.append(block)
            new_component_path.append(new_path)
        self.component_path = new_component_path

    def get_text(self):
        if not self.component_path:
            return ''
        text = list()
        for path in self.component_path:
            for block in path:
                text.append(block.get_text())
            text.append(f"{'='*64}")
        return '\n'.join(text)

    def check_validity(self, blocks=None):
        if not self.component_path:
            self.analyze(blocks)
        for path in self.component_path:
            if self._check_valid_path(path):
                self.valid_path.append(path)
        return self.is_valid

    def _check_valid_path(self, path):
        # Step 1 - Create a list of all smart components in the path
        components = [component for block in path for component in block.get_conditional()]
        # Step 2 - Create a 2D list of matching items
        unique_list = list()
        duplicates = list()  # 2D list with each row containing a list of matching component.
        for component in components:
            if component not in unique_list:
                unique_list.append(component)
                continue
            index = self._check_duplicate(duplicates, component)
            if index == self.NOT_IN_DUPLICATES:  # If not added in duplicates yet
                # Add the component and the unique component from the unique set
                duplicate = list()
                duplicate.append(component)
                for unique_component in unique_list:
                    if unique_component == component:
                        duplicate.append(unique_component)
                duplicates.append(duplicate)
            else:  # It is already added in the duplicate. It is a triplicate or more!
                duplicates[index].append(component)
        # Step 3 - Check all matching items for valid conditions
        for duplicate in duplicates:
            for index1, index2 in combinations(range(len(duplicate)), 2):
                if not self._compare_components(duplicate[index1], duplicate[index2]):
                    return False
        return True

    def _check_duplicate(self, duplicates, component):
        for index, duplicate in enumerate(duplicates):
            if component in duplicate:
                return index
        return self.NOT_IN_DUPLICATES

    @staticmethod
    def _compare_components(component1, component2):
        if component1.condition == component2.condition and component1.direction != component2.direction:
            return False
        # TODO Fix for opposite condition later, once the TM bit issue is resolved.
        if component1.condition != component2.condition and component1.direction == component2.direction:
            return False
        return True


class Analyze:
    def __init__(self, head, tail, blocks):
        self.head = head
        self.tail = tail
        self.blocks = blocks
        try:
            self._paths = self.search(blocks[head])
        except KeyError:
            self._paths = list()
        self._replace = list()

    def search(self, block, asm_path=None):
        if asm_path:
            asm_path.append(block.label)
        else:
            asm_path = [block.label]
        path_labels = [label for label in block.get_next() if label not in asm_path]
        path_labels.extend([label for label in block.get_calls() if label not in asm_path])
        found_paths = list()
        for label in path_labels:
            if label == self.tail:
                found_path = asm_path.copy()
                found_path.append(label)
                found_paths.append(found_path)
            else:
                search_paths = self.search(self.blocks[label], asm_path.copy())
                found_paths.extend(search_paths)
        return found_paths

    def get_count(self):
        return len(self._paths)

    def get_all(self):
        return self._paths

    def get_normal_path(self):
        normal_len, normal = self._get_max(self._paths)
        return normal[0] if normal_len else list()

    def get_text(self, path=None):
        path = self.get_normal_path() if not path else path
        text = list()
        for index, label in enumerate(path):
            # Get all conditions of the path (Exclude fall down)
            conditional = [component for component in self.blocks[label].components.list_values
                           if component.conditional]
            text.append(label)
            # Get the true components that goes or falls down to any where in the path
            true_components = [component for component in self.blocks[label].components.list_values
                               if set(component.get_goes()) & set(path[index + 1:])] \
                if index + 1 < len(path) else list()
            # For all components, IGNORE the components that go to / fall down within the path
            # and display everything else.
            # Continue only till the last component that go to / fall down within the path.
            for component in conditional:
                if component in true_components:
                    if component == true_components[-1] and self.blocks[label].fall_down not in path[index + 1:]:
                        # Last component that goes to the path. (Does NOT fall down to the path)
                        # Do NOT check for other conditional components after this
                        text.append(f"{' '*10}{component.get_text(True, path[index + 1:])}")
                        break
                    else:
                        text.append(f"{' '*10}{component.get_text(False)} **CAN GO WITHIN PATH ON OPPOSITE**")
                elif set(component.get_goes()) & set(path[: index + 1]):
                    text.append(f"{' '*10}{component.get_text(False)} **LOOPS ON OPPOSITE**")
                elif label != path[-1] or self.blocks[label].ends_in_program_exit():
                    text.append(f"{' '*10}{component.get_text(False)}")
            # If the last block ends in exit then display the exit condition
            if label == path[-1] and self.blocks[label].ends_in_program_exit():
                component = self.blocks[label].components.list_values[-1]
                end_text = [f"{' '*10}{component.command}"]
                if component.is_key_value:
                    msg = next((operand.key_value['value'] for operand in component.operands.list_values
                                if operand.key_value and operand.key_value['key'] == 'MSG'), None)
                else:
                    msg = next((operand.variable for operand in component.operands.list_values
                                if operand.variable), None)
                if msg:
                    end_text.append(msg)
                text.append(' '.join(end_text))
        return '\n'.join(text)

    def update(self, paths):
        self._paths = paths

    def normalize(self, paths=None):
        if paths is None:
            paths = self._paths
        max_len, max_paths = self._get_max(paths)
        if not max_len:
            return paths
        other_paths = list()
        for asm_path in paths:
            if len(asm_path) == max_len:
                continue
            found = next((max_path for max_path in max_paths if set(asm_path).issubset(max_path)), None)
            if not found:
                other_paths.append(asm_path)
        max_paths.extend(self.normalize(other_paths))
        return max_paths

    def remove_paths_with_one_difference(self, paths=None):
        if paths is None:
            paths = self._paths
        max_len, max_paths = self._get_max(paths)
        if not max_len:
            return paths
        other_paths = [asm_path for asm_path in paths if asm_path not in max_paths]
        delete_paths = list()
        for path1, path2 in combinations(range(len(max_paths)), 2):
            if max_paths[path1] in delete_paths or max_paths[path2] in delete_paths:
                continue
            labels = list(set(max_paths[path1]) - set(max_paths[path2]))
            if len(labels) != 1:
                continue
            index = max_paths[path1].index(labels[0])
            if max_paths[path1][index - 1] == max_paths[path2][index - 1] and \
               max_paths[path1][index + 1] == max_paths[path2][index + 1]:
                remove_path = max_paths[path2]
                keep_path = max_paths[path1]
                delete_paths.append(remove_path)
                replace = {'removed': remove_path[index], 'kept': keep_path[index]}
                if replace not in self._replace:
                    self._replace.append(replace)
        max_paths = [asm_path for asm_path in max_paths if asm_path not in delete_paths]
        max_paths.extend(self.remove_paths_with_one_difference(other_paths))
        return max_paths

    @staticmethod
    def _get_max(paths):
        if not paths:
            return 0, list()
        max_len = max([len(asm_path) for asm_path in paths])
        max_paths = [asm_path for asm_path in paths if len(asm_path) == max_len]
        return max_len, max_paths

    def critical_paths(self):
        paths = self._paths
        if len(paths) <= 1:
            return paths
        min_len = min([len(asm_path) for asm_path in paths])
        # Identify the last common label from start
        start = self.head
        for index in range(min_len):
            labels = [asm_path[index] for asm_path in paths]
            if not all(label == labels[0] for label in labels):
                break
            start = labels[0]
        # Identify the last common label from end
        end = self.tail
        for index in range(-1, -min_len - 1, -1):
            labels = [asm_path[index] for asm_path in paths]
            if not all(label == labels[0] for label in labels):
                break
            end = labels[0]
        # Return the sliced path from start to end for each path
        return [asm_path[asm_path.index(start): asm_path.index(end) + 1] for asm_path in paths]

    def get_replaced_labels(self):
        if not self._replace:
            return 'No path removed.'
        text = list()
        for replace in self._replace:
            text.append(f"Removed: {replace['removed']}. Kept: {replace['kept']}.")
        return '\n'.join(text)
