from firestore_model import init_firestore_db
from models import Path, Block, Reference, References
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
    # pgm.first_pass()
    # for line in pgm.lines:
    #     print(f'L={line.label}, C={line.command}, O={line.operands}')
    # pgm.create_blocks()
    # for key in pgm.blocks:
    #     print(pgm.blocks[key].get_str())
    # pgm.create_paths()
    # for path in pgm.paths:
    #     print(show(path, pgm.blocks))
    # print(len(pgm.paths))

    # For ETA5
    pgm_name = 'eta5'
    pgm = AssemblerProgram(pgm_name)
    save = False
    pgm = create(pgm, save)
    for key in pgm.blocks:
        print(pgm.blocks[key].get_str())
    for path in pgm.paths:
        print(show(path, pgm.blocks))
    print(len(pgm.paths))

    # Analyze
    # pgm_name = 'eta5'
    # pgm = AssemblerProgram(pgm_name)
    # pgm.load_blocks()
    # paths = Path.query(name=pgm.name, head='$$eta5$$')
    # paths.sort(key=lambda item: item.weight)
    # for path in paths[:11]:
    #     print(show(path, pgm.blocks))

    # Test
    # ref = References(goes='A')
    # ref.add(goes='C', calls='B')
    # block = Block('AAA')
    # block.add_references(ref)
    # block.update()
    # block = Block.query(label='AAA')[0]
    # print(block.get_str())

