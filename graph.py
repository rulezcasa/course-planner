"""Part 1: graph construction and topological sort.

Written by keerthana.
"""
from collections import deque

class CycleError(Exception):
    def __init__(self, cycle_courses):
        self.cycle_courses = list(cycle_courses)
        super().__init__(f"Prerequisite cycle among: {self.cycle_courses}")

def build_graph(courses, pairs):    
    course_set = set(courses)
    if len(course_set) != len(courses):
        raise ValueError("Duplicate courseId found in courses")
    unlocks = {course: [] for course in courses}
    prereqs = {course: [] for course in courses}
    seen_pairs = set()
    for pair in pairs:
        a,b = pair[0],pair[1]
        if a not in course_set or b not in course_set:
            raise ValueError("Pair not in courses")
        if (a,b) in seen_pairs:
            raise ValueError("Duplicate pair")
        seen_pairs.add((a,b))
        unlocks[a].append(b)
        prereqs[b].append(a)
    return unlocks,prereqs

def topological_sort(courses, unlocks, prereqs):
    in_degree = { course : len(prereqs[course]) for course in courses}
    queue = deque([course for course in courses if in_degree[course] == 0])
    ordered = []
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for next_course in unlocks[current]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    if len(ordered) != len(courses):
        leftover_courses = [c for c in courses if in_degree[c] > 0]
        raise CycleError(leftover_courses)
    return ordered