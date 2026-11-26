"""Tests for Part 1. Run with:  python3 -m unittest -v test_graph"""

import os
import unittest

from graph import CycleError, build_graph, topological_sort
from loader import load_program, read_program_file

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "test_data")


def path(name):
    return os.path.join(DATA, name + ".json")


def assert_valid_order(tc, courses, pairs, order):
    """Every course appears exactly once, and every A comes before its B."""
    tc.assertEqual(sorted(order), sorted(courses), "order must contain each course once")
    pos = {c: i for i, c in enumerate(order)}
    for a, b in pairs:
        tc.assertLess(pos[a], pos[b], f"{a} must come before {b}")


class TestBuildGraph(unittest.TestCase):
    def test_edges_both_directions(self):
        unlocks, prereqs = build_graph(["A", "B", "C"], [["A", "B"], ["A", "C"]])
        self.assertEqual(sorted(unlocks["A"]), ["B", "C"])
        self.assertEqual(prereqs["B"], ["A"])
        self.assertEqual(prereqs["A"], [])
        self.assertEqual(unlocks["C"], [])

    def test_every_course_is_a_key(self):
        unlocks, prereqs = build_graph(["A", "B"], [])
        self.assertEqual(set(unlocks), {"A", "B"})
        self.assertEqual(set(prereqs), {"A", "B"})

    def test_unknown_course_rejected(self):
        with self.assertRaises(ValueError):
            load_program(path("unknown_course"))

    def test_duplicate_pair_rejected(self):
        with self.assertRaises(ValueError):
            load_program(path("duplicate_pair"))

    def test_duplicate_course_rejected(self):
        with self.assertRaises(ValueError):
            load_program(path("duplicate_course"))


class TestTopologicalSort(unittest.TestCase):
    VALID = ["chain", "independent", "fan_out", "diamond", "all_completed", "empty"]

    def test_valid_programs_give_valid_order(self):
        for name in self.VALID:
            with self.subTest(program=name):
                _, courses, pairs = read_program_file(path(name))
                program = load_program(path(name))
                assert_valid_order(self, courses, pairs, program.order)

    def test_chain_order_is_forced(self):
        self.assertEqual(load_program(path("chain")).order, ["A", "B", "C", "D"])

    def test_cycle_rejected_at_load(self):
        with self.assertRaises(CycleError) as ctx:
            load_program(path("cycle"))
        self.assertEqual(sorted(ctx.exception.cycle_courses), ["A", "B", "C"])

    def test_cycle_reports_only_unorderable_courses(self):
        with self.assertRaises(CycleError) as ctx:
            load_program(path("cycle_with_tail"))
        bad = set(ctx.exception.cycle_courses)
        self.assertTrue({"A", "B", "C"} <= bad)       # the cycle itself
        self.assertNotIn("X", bad)                    # X and Y can be ordered
        self.assertNotIn("Y", bad)

    def test_self_loop_rejected(self):
        with self.assertRaises((CycleError, ValueError)):
            load_program(path("self_loop"))

    def test_real_programs(self):
        for name in ["course_map", "aerospace_course_map"]:
            p = os.path.join(HERE, name + ".json")
            with self.subTest(program=name):
                _, courses, pairs = read_program_file(p)
                assert_valid_order(self, courses, pairs, load_program(p).order)


if __name__ == "__main__":
    unittest.main()
