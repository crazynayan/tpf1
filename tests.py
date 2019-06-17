import unittest
from firestore_model import init_firestore_db
from assembler import AssemblerProgram
from models import Block, Path


class TestTPF(unittest.TestCase):
    def setUp(self) -> None:
        init_firestore_db('tpf1-key.json')

    def test_eta5_refs(self):
        pgm_name = 'eta5'
        pgm = AssemblerProgram(pgm_name)
        pgm.create_blocks()
        pgm.create_paths()
        for _, block in pgm.blocks.items():
            db_block = Block.query_first(name=pgm_name, label=block.label)
            self.assertListEqual(db_block.get_next(), block.get_next(), block.get_str())
            self.assertEqual(db_block.get_str(), block.get_str(), block.get_str())

    def test_path_count(self):
        self.assertEqual(1550, len(Path.query(name='eta5')))
