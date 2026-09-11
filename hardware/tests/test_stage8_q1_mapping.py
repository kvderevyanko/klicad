"""Regression protection for the Stage-8 Q1 schematic net mapping."""
import ast
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "generate_stage8_placement.py"
EXPECTED_Q1_PAD_NETS = {"1": "Q1_GATE", "2": "BUCK_IN", "3": "BAT_SW"}


class Stage8Q1MappingTests(unittest.TestCase):
    def test_q1_mapping_is_authoritative_and_used(self):
        tree = ast.parse(SOURCE.read_text())
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "Q1_PAD_NETS"
                               for target in node.targets)]
        self.assertEqual(len(assignments), 1)
        self.assertEqual(ast.literal_eval(assignments[0].value), EXPECTED_Q1_PAD_NETS)

        q1_connects = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Name) and node.func.id == "connect"
                       and len(node.args) == 2 and isinstance(node.args[0], ast.Name)
                       and node.args[0].id == "q1"]
        self.assertEqual(len(q1_connects), 1)
        self.assertIsInstance(q1_connects[0].args[1], ast.Name)
        self.assertEqual(q1_connects[0].args[1].id, "Q1_PAD_NETS")

        self.assertIn('"/BAT_SW"', SOURCE.read_text())


if __name__ == "__main__":
    unittest.main()
