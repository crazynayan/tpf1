from firestore_model import init_firestore_db
from assembler import AssemblerProgram
from side_car import Analyze


if __name__ == '__main__':
    init_firestore_db('tpf1-key.json')
    # # For ETA5
    pgm = AssemblerProgram('eta5')
    pgm.create_nodes()
    g = Analyze(pgm.nodes)
    g.show('ETA5380-1')
