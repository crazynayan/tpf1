from firestore_model import init_firestore_db
from models import Path, Block
from assembler import AssemblerProgram


def show(name, asm_path, blocks):
    path = [f'{name}({len(asm_path)}) = ']
    for label in asm_path:
        path.append(label)
        if blocks[label].function_calls:
            fc_labels = [f'{fc_label}, ' for fc_label in blocks[label].function_calls]
            fc_str = ''.join(fc_labels)[:-2]
            path.append(f'*({fc_str})')
        path.append('->')
    return ''.join(path)[:-2]


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
    #     print(pgm.blocks[key])
    # pgm.create_paths()
    # for a_path in pgm.paths:
    #     print(show(pgm_name, a_path, pgm.blocks))
    # print(len(pgm.paths))

    # For ETA5
    pgm_name = 'eta5'
    pgm = AssemblerProgram(pgm_name)
    # Block.delete_all()
    # pgm.create_blocks(save=True)
    # for key in pgm.blocks:
    #     print(pgm.blocks[key])
    # Path.delete_all()
    pgm.create_paths(save=False)
    for a_path in pgm.paths:
        print(show(pgm_name, a_path, pgm.blocks))
    print(len(pgm.paths))
    # paths = Path.query(name=pgm_name)
    # print(len(paths))
    # for path in paths:
    #     print(path.path)


