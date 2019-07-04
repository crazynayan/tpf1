from firestore_model import init_firestore_db
from models import Path, Block  # ,  Reference, References, Component, Operands
from assembler import AssemblerProgram
from side_car import Analyze


def analyze_path(start, end):
    pgm = AssemblerProgram('eta5')
    pgm.create_blocks()
    paths = Analyze(start, end, pgm.blocks)
    print(f'Before normalization: {paths.get_count()}')
    paths.update(paths=paths.normalize())
    print(f'After normalization : {paths.get_count()}')
    paths.update(paths=paths.remove_paths_with_one_difference())
    print(f'After removal       : {paths.get_count()}')
    for path in paths.get_all():
        print(path)
    print(paths.get_replaced_labels())
    critical = paths.critical_paths()
    print('Critical path')
    for path in critical:
        print(path)
    print('\nNormal Path Text')
    paths.update(smart_blocks=paths.create_smart_blocks())
    print(paths.get_smart_text())
    # if len(critical) >= 1:
    #     print('\nCritical Path Text')
    #     for path in critical:
    #         print(path)
    #     for path in critical:
    #         print('='*165)
    #         print(paths.get_smart_text(path))


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


def show_last_path(asm_paths=None, blocks=None):
    if not asm_paths:
        asm_paths = Path.query(head='$$eta5$$')
    exit_labels = list()
    merge_labels = list()
    for path in asm_paths:
        last = path.path[-1]
        if f'{last:8}' not in [label[0] for label in exit_labels] and \
           f'{last:8}' not in [label[0] for label in merge_labels]:
            count = len([path for path in asm_paths if path.path[-1] == last])
            block = blocks[last] if blocks else Block.query_first(label=last)
            cmd = block.components[-1].command + ' ' + str(block.components[-1].operands[1])
            if path.exit_on_program:
                exit_labels.append((f'{last:8}', count, f'{cmd:20}'))
            else:
                merge_labels.append((f'{last:8}', count, f'L:{path.exit_on_loop:2}', f'M:{path.exit_on_merge:2}'))
    merge_labels.sort(key=lambda item: item[0])
    for label in exit_labels:
        print(label)
    for label in merge_labels:
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
    # # for key in pgm.blocks:
    # #     print(pgm.blocks[key].get_str())
    # pgm.paths.sort(key=lambda item: item.path)
    # paths = pgm.paths
    # for path in paths:
    #     print(show(path, pgm.blocks))
    # # for path in paths:
    # #     print(ComponentPath(path).get_text())
    # print(len(paths))
    # show_last_path(paths, pgm.blocks)
    # for path in paths:
    #     print(f"{'-'*25}{path.head} to {path.tail}{'-'*25}")
    #     for index, label in enumerate(path.path):
    #         if label == path.tail:
    #             if path.exit_on_program:
    #                 print(f"{label:10}{pgm.blocks[label].components[-1].command}")
    #         else:
    #             print(pgm.blocks[label].get_text(path.path[index + 1]))

    # Analyze
    # pgm = AssemblerProgram('eta5')
    # pgm.create_blocks()
    # commands = {component.command for key in pgm.blocks for component in pgm.blocks[key].components.list_values}
    # for command in commands:
    #     print(command)
    # paths = Path.query(weight=33993)
    # for index, label in enumerate(paths[0].path[:-1]):
    #     print(pgm.blocks[label].get_text(paths[0].path[index + 1]))
    analyze_path('$$eta5$$', 'ETA5250')

