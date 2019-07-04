from itertools import combinations
from models import Component, Block


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


class Analyze:
    def __init__(self, head, tail, blocks):
        self.head = head
        self.tail = tail
        self.blocks = blocks
        self._smart_blocks = list()
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

    def create_smart_blocks(self, path=None):
        path = self.get_normal_path() if not path else path
        smart_blocks = list()
        # Step 1 - Create a list SmartBlocks for each label in the path
        for index, label in enumerate(path):
            prior_path = path[: index + 1]
            follow_path = path[index + 1:] if label != path[-1] else list()
            smart_blocks.append(SmartBlock(self.blocks[label], prior_path, follow_path))
        # Step 2 - Get the operands that are used in relevant conditions
        smart_operands = [operand for block in smart_blocks
                          for component in block.components
                          for operand in component.operands.list_values
                          if component.is_conditional and
                          component.tag not in [component.WITHIN_PATH, component.LOOP] and
                          not operand.key_value and operand.constant is None]
        # Step 3 - Update the display parameter of the components in SmartBlocks
        smart_blocks.reverse()
        for block in smart_blocks:
            block.components.reverse()

        for main_block_index, block in enumerate(smart_blocks):
            for main_index, component in enumerate(block.components):
                if not component.is_conditional:
                    continue
                if block.label == 'ETA5300':
                    a = 1
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

        smart_blocks.reverse()
        for block in smart_blocks:
            block.components.reverse()

        return smart_blocks

    def get_smart_text(self, path=None):
        if path:
            smart_blocks = self.create_smart_blocks(path)
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

    def update(self, paths=None, smart_blocks=None):
        self._paths = paths if paths is not None else self._paths
        self._smart_blocks = smart_blocks if smart_blocks is not None else self._smart_blocks

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

    def get_smart_operands(self):
        return [operand for block in self._smart_blocks
                for component in block.components
                for operand in component.operands.list_values
                if component.is_conditional and
                component.tag not in [component.WITHIN_PATH, component.LOOP] and
                not operand.key_value and operand.constant is None]

