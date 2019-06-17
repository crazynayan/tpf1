from firestore_model import init_firestore_db
from models import Path, Block  # ,  Reference, References, Component, Operands
from assembler import AssemblerProgram


def show(asm_path, blocks):
    a_path = [f'{asm_path} = ']
    for label in asm_path.path:
        a_path.append(label)
        if blocks[label].get_calls():
            fc_labels = [f'{fc_label},' for fc_label in blocks[label].get_calls()]
            fc_str = ''.join(fc_labels)[:-1]
            a_path.append(f'|>({fc_str})')
        if blocks[label].get_loops():
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

    # For ETA5
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

    # Analyze
    pgm_name = 'eta5'
    pgm = AssemblerProgram(pgm_name)
    pgm.load_blocks()
    # commands = {component.command for key in pgm.blocks for component in pgm.blocks[key].components.list_values}
    # for command in commands:
    #     print(command)
    # paths = Path.query(name=pgm.name, head='$$eta5$$')
    # paths.sort(key=lambda item: item.weight)
    # for path in paths[:11]:
    #     print(show(path, pgm.blocks))
    path = Path.query_first(name=pgm_name, head='$$eta5$$', weight=4595)
    print(show(path, pgm.blocks))
    for label in path.path:
        print(pgm.blocks[label].get_str())

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
