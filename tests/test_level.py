# File: tests/test_level.py
import unittest
import os
from level import Level

class TestLevel(unittest.TestCase):
    def test_parse_csv(self):
        test_file = os.path.join('data', 'level1.csv')
        lvl = Level(test_file)
        self.assertTrue(len(lvl.platforms) > 0)
        self.assertTrue(len(lvl.enemy_spawns) > 0)
        self.assertTrue(len(lvl.coin_spawns) > 0)
        self.assertTrue(isinstance(lvl.player_spawn, tuple))

if __name__ == '__main__':
    unittest.main()
