from firestore_model import init_firestore_db
from models import Path, AssemblerProgram, Block


if __name__ == '__main__':
    pgm_name = 'eta5'
    init_firestore_db('tpf1-key.json')
    # paths = Path.query(name=pgm_name)
    # for path in paths:
    #     path.delete()
    pgm = AssemblerProgram(pgm_name)
    # Block.delete_all()
    # pgm.create_blocks()
    # Path.delete_all()
    # pgm.create_paths(save=True)
    # paths = Path.query(name=pgm_name)
    # print(len(paths))
    # for path in paths:
    #     print(path.path)
    # for path in pgm.paths:
    #     print(f'{len(path)} -> {path}')
    # print(len(pgm.paths))
