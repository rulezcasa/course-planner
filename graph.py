"""
Graph construction and topological sort.

Contributor : Keerthana 

Note for instructor : Added appropriate docstrings for logic and explanation
"""

from collections import deque

"""
Custom error class for cycles
"""
class CycleError(Exception):
    def __init__(self, cycle_courses):
        self.cycle_courses = list(cycle_courses)
        super().__init__(f"Prerequisite cycle among: {self.cycle_courses}")


"""
Function to build graph as adjacency list

Input : List of courses, List of pairs ([A,B] denotes A comes before B)
Output : 
    1. unlocks : Forward adjacency list denoting the courses unlocked after completing current. 
    2. prereqs : Reverse adjacency list denoting the prerequisites of a current course.
    
    Building both lists at load time enables faster preqrequiste lookups for the planner without scanning the graph everytime i.e O(V+E) vs O(V.V(V+E) respectively. 
"""
def build_graph(courses, pairs):    
    course_set = set(courses)
    if len(course_set) != len(courses):
        raise ValueError("Duplicate courseId found in courses")
    unlocks = {course: [] for course in courses}
    prereqs = {course: [] for course in courses}
    seen_pairs = set()
    for pair in pairs:
        a,b = pair[0],pair[1]
        if a not in course_set or b not in course_set:          # Pair validation for presence
            raise ValueError("Pair not in courses")
        if (a,b) in seen_pairs:                                 # Pair validation for duplicates
            raise ValueError("Duplicate pair")
        seen_pairs.add((a,b))
        unlocks[a].append(b)
        prereqs[b].append(a)
    return unlocks,prereqs


"""
Function to toplogical sort

Input : List of courses, forward adjacency list
Output : List of ordered courses OR CycleError if cycle present
"""
def topological_sort(courses, unlocks):
    in_degree = {course: 0 for course in courses}
    for course in courses:
        for next_course in unlocks[course]:
            in_degree[next_course] += 1
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