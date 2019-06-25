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

    def get_text(self, label):
        return self._component.get_text(self.direction, label)


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
            text.append(f"{' '*10}{component.get_text(self.next_label)}")
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
