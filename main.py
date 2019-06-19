from firestore_model import init_firestore_db
from models import Path, Block  # ,  Reference, References, Component, Operands
from assembler import get_text_from_path, AssemblerProgram
from side_car import ComponentPath


def show(asm_path, blocks):
    a_path = [f'{asm_path} = ']
    for label in asm_path.path:
        a_path.append(label)
        if blocks[label].get_calls():
            fc_labels = [f'{fc_label},' for fc_label in blocks[label].get_calls()]
            fc_str = ''.join(fc_labels)[:-1]
            a_path.append(f'|>({fc_str})')
        if blocks[label].get_loops() and label == asm_path.path[-1]:
            fc_labels = [f'{fc_label},' for fc_label in blocks[label].get_loops()]
            fc_str = ''.join(fc_labels)[:-1]
            a_path.append(f'<>({fc_str})')
        a_path.append('->')
    return ''.join(a_path)[:-2]


def create(a_pgm, a_save=False):
    if a_save:
        Block.delete_all()
        a_pgm.create_blocks()
        Path.delete_all()
        a_pgm.create_paths(a_save)
    else:
        a_pgm.create_blocks()
        a_pgm.create_paths()
    return a_pgm


def show_last_path(paths=None, blocks=None):
    if not paths:
        paths = Path.query(head='$$eta5$$')
    labels = list()
    for path in paths:
        last = path.path[-1]
        if last not in [label[0] for label in labels]:
            count = len([path for path in paths if path.path[-1] == last])
            block = blocks[last] if blocks else Block.query_first(label=last)
            cmd = block.components[-1].command + ' ' + str(block.components[-1].operands[1])
            labels.append((last, count, cmd, path.exit_on_program, path.exit_on_loop))
    labels.sort(key=lambda item: item[1])
    for label in labels:
        print(label)


if __name__ == '__main__':
    init_firestore_db('tpf1-key.json')
    # For temp
    # pgm_name = 'temp'
    # pgm = AssemblerProgram(pgm_name)
    # pgm.create_blocks()
    # pgm.create_paths()
    # for key in pgm.blocks:
    #     print(pgm.blocks[key].get_str())
    # for path in pgm.paths:
    #     print(show(path, pgm.blocks))
    # print(len(pgm.paths))

    # # For ETA5
    # pgm_name = 'eta5'
    # pgm = AssemblerProgram(pgm_name)
    # save = False
    # pgm = create(pgm, save)
    # for key in pgm.blocks:
    #     print(pgm.blocks[key].get_str())
    # pgm.paths.sort(key=lambda item: item.weight)
    # for path in pgm.paths:
    #     print(show(path, pgm.blocks))
    # print(len(pgm.paths))
    # # show_last_path(pgm.paths, pgm.blocks)
    # # with open('path_text.txt', 'w') as file:
    # #     for path in pgm.paths:
    # #         if path.exit_on_program:
    # #             file.write(f"{'-'*31}{path.weight}{'-'*(31-len(str(path.weight)))}\n")
    # #             file.write(f"{get_text_from_path(path, pgm.blocks)}\n")
    # #     print('File created.')

    # Analyze
    pgm = AssemblerProgram('eta5')
    pgm.create_blocks()
    # commands = {component.command for key in pgm.blocks for component in pgm.blocks[key].components.list_values}
    # for command in commands:
    #     print(command)
    paths = Path.query(weight=51)
    paths.sort(key=lambda item: item.weight)
    for path in paths:
        print(f"{'-'*31}{path.weight}{'-'*(31-len(str(path.weight)))}")
        print(get_text_from_path(path, pgm.blocks))
    cp = ComponentPath(paths[0])
    cp.analyze(pgm.blocks)
    for cs in cp.component_path:
        print('-'*64)
        print(cs)
    print(len(cp.component_path))


    # Test
    # ref = References(goes='A')
    # ref.add(goes='C', calls='B')
    # ref.add(goes='A', calls='A', loops='A')
    # block = Block('AAA')
    # block.add_references(ref)
    # block.components.append(Component('L', ['R1', 'CE1CR1']))
    # block.components.append(Component('LA', ['R7', 'EBW040']))
    # block.components.append(Component('TM', ['WA0ET4', '#WA0TTY']))
    # block.update()
    # block = Block.query(label='AAA')[0]
    # print(block.get_str())

