from v1.firestore_model import init_firestore_db
from v1.assembler import AssemblerProgram
from v1.side_car import Analyze

if __name__ == '__main__':
    init_firestore_db('v1/tpf1-key.json')
    # For ETA5
    pgm = AssemblerProgram('eta5')
    pgm.set_file_name('v1/')
    pgm.create_nodes()
    g = Analyze(pgm.nodes)
    g.show('ETA5380-1')
    # mac = Macro()
    # print(mac.files)
    # mac.load('PR001W')
    # for _, field in mac.data_map.items():
    #     print(f'{field.label:10} {field.dsp:03x} {field.length:3}')
