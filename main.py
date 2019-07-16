from firestore_model import init_firestore_db
from assembler import AssemblerProgram
from side_car import Analyze


if __name__ == '__main__':
    init_firestore_db('tpf1-key.json')
    # # For ETA5
    pgm = AssemblerProgram('eta5')
    pgm.create_nodes()
    # for key in pgm.nodes:
    #     print(pgm.nodes[key].get_str())
    # print(len(pgm.nodes))
    # exit_nodes = [pgm.nodes[key] for key in pgm.nodes if pgm.nodes[key].is_program_exit]
    # for node in exit_nodes:
    #     print(node.get_str())
    g = Analyze(pgm.nodes)
    for key in g.nodes:
        print(g.nodes[key].get_str())
    # print(len(g.nodes))
    g.show('ETA9027X-7')

    # Analyze
    # # pgm = AssemblerProgram('eta5')
    # # pgm.create_blocks()
    # # commands = {component.command for key in pgm.blocks for component in pgm.blocks[key].components.list_values}
    # # for command in commands:
    # #     print(command)
    # # paths = Path.query(weight=33993)
    # # for index, label in enumerate(paths[0].path[:-1]):
    # #     print(pgm.blocks[label].get_text(paths[0].path[index + 1]))
    # analyze_path('$$eta5$$', 'ETA5250')
