from itertools import product
from models import Block


class SmartComponent:
    def __init__(self, component):
        self._component = component
        self.conditional = False
        self.direction = False
        if component.get_next() and not component.is_exit:
            self.conditional = True

    def get(self):
        return self._component


class SmartComponents:
    def __init__(self):
        self._components = list()

    def append(self, component):
        self._components.append(SmartComponent(component))

    def get(self):
        return [component.get() for component in self._components]


class ComponentPath:
    def __init__(self, path):
        self.path = path  # instance of Path object
        self.component_path = list()  # different combination of the list of components in the path

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
            # Get a list of component path. Each component path has a list of components.
            # component -> components -> component_path -> component_paths
            component_path = blocks[label].get_path(self.path.path[index + 1])
            component_paths.append(component_path)
        # Create component path
        self.component_path = list(product(*component_paths))
