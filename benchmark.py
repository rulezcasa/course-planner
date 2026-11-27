"""
Measured runtime vs theoretical runtime.

Contributor : Suharrsh

Note for instructor : Run with `python benchmark.py`. Graphs are generated in memory with a
fixed seed so the results are repeatable. For each size we divide the measured time by the
theoretical operation count. If that value (ns/op) stays roughly flat as the input grows,
the code runs in the predicted time. The "x prev" column is the time ratio to the previous
row: about 2 when the work doubles (linear), about 4 when it quadruples (quadratic).
"""

import random
import time
from graph import build_graph, topological_sort
from loader import Program
from planner import Student, needed_courses, plan_semesters

random.seed(255)


"""
Function to generate a random program with no cycles

Input : Number of courses, maximum prerequisites per course
Output : List of courses, list of pairs ([A,B] denotes A comes before B)
"""
def random_program(num_courses, max_prereqs):
    courses = [f"C{i}" for i in range(num_courses)]
    pairs = []
    for j in range(1, num_courses):
        count = random.randint(0, min(max_prereqs, j))
        for i in random.sample(range(j), count):      # prereqs only from earlier courses, so no cycles
            pairs.append([courses[i], courses[j]])
    return courses, pairs


"""
Function to generate a straight chain C0 -> C1 -> ... (worst case for the number of semesters)

Input : Number of courses
Output : List of courses, list of pairs
"""
def chain_program(num_courses):
    courses = [f"C{i}" for i in range(num_courses)]
    pairs = [[courses[i - 1], courses[i]] for i in range(1, num_courses)]
    return courses, pairs


"""
Function to time graph construction plus Kahn's topological sort (best of several runs)

Input : List of courses, list of pairs, number of runs
Output : Best time in seconds
"""
def time_load(courses, pairs, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        unlocks, prereqs = build_graph(courses, pairs)
        topological_sort(courses, unlocks)
        best = min(best, time.perf_counter() - start)
    return best


"""
Function to time plan_semesters for a student who needs every course (best of several runs)

Input : List of courses, list of pairs, semester limit, number of runs
Output : Best time in seconds, number of semesters in the plan
"""
def time_plan(courses, pairs, limit, repeats=3):
    unlocks, prereqs = build_graph(courses, pairs)
    order = topological_sort(courses, unlocks)
    program = Program("Bench", "BENCH", courses, {c: c for c in courses}, unlocks, prereqs, order, limit)
    needed = needed_courses(courses, prereqs, courses, set())
    best = float("inf")
    for _ in range(repeats):
        student = Student("Bench", program, [], courses, needed)   # fresh student, planning changes it
        start = time.perf_counter()
        semesters = plan_semesters(student, limit, order)
        best = min(best, time.perf_counter() - start)
    return best, len(semesters)


"""
Function to print one table of results

Input : Title, theoretical formula, rows of (V, E, S, seconds, ops)
Output : None (prints the table)
"""
def print_table(title, formula, rows):
    print(f"\n{title}   theory: {formula}")
    print(f"{'V':>7} {'E':>7} {'S':>6} {'time (ms)':>10} {'ops':>12} {'ns/op':>7} {'x prev':>7}")
    previous = None
    for v, e, s, seconds, ops in rows:
        growth = f"{seconds / previous:.2f}" if previous else "-"
        print(f"{v:>7} {e:>7} {s:>6} {seconds * 1000:>10.2f} {ops:>12} {seconds * 1e9 / ops:>7.1f} {growth:>7}")
        previous = seconds


if __name__ == "__main__":
    rows = []
    for v in [2000, 4000, 8000, 16000, 32000, 64000]:
        courses, pairs = random_program(v, 3)
        rows.append((v, len(pairs), 1, time_load(courses, pairs), v + len(pairs)))
    print_table("1. build_graph + topological_sort (random DAG)", "O(V + E)", rows)

    for title, make in [("2. plan_semesters (random DAG, limit 3)", lambda v: random_program(v, 3)),
                        ("3. plan_semesters (chain, limit 3, S = V)", chain_program)]:
        rows = []
        for v in [250, 500, 1000, 2000, 4000]:
            courses, pairs = make(v)
            seconds, s = time_plan(courses, pairs, 3)
            rows.append((v, len(pairs), s, seconds, s * (v + len(pairs))))
        print_table(title, "O(S * (V + E))", rows)
