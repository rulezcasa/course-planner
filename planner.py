"""
Student progress, available courses and semester planning.

Contributor : Harish

Note for instructor : Added appropriate docstrings for logic and explanation
"""

from collections import deque

"""
Custom class and methods holding student's progress
"""
class Student:
    def __init__(self, name, program, completed, targets, needed):
        self.name = name                        # Student name
        self.program = program                  # Program pursuing
        self.completed = set(completed)         # Completed courese (updated every semester)
        self.targets = set(targets)             # Courses the student wants to take
        self.needed = needed                    # Targets plus missing prerequisites, from needed_courses()
        self.available = []                     # Courses available
        self.semesters = []                     # Future semesters and coureses
        self.refresh_available()                # Available state refresh

    """
    Class instance method to refresh available courses based on completed courses

    Input : None
    Output : None
    """
    def refresh_available(self):
        self.available = available(self.needed, self.program.prereqs, self.completed)

    """
    Class instance method to update completed courses and refreshes available courses

    Input : Set of completed courses
    Output : None
    """
    def complete(self, courses):
        self.completed.update(courses)
        self.refresh_available()


"""
Function that returns the courses a student still has to take based on preference i.e target

Input : List of courses, reverse adjacency list, set of target courses, set of completed courses
Output : List of target courses plus every prerequisite they still need (file order), excluding completed ones
"""
def needed_courses(courses, prereqs, targets, completed):
    needed = set()
    queue = deque()
    #BFS backwards over prereqs starting from the targets to find prerequisites of prerequisites. O(V+E).
    for course in targets:
        if course not in completed and course not in needed:
            needed.add(course)
            queue.append(course)
    while queue:
        current = queue.popleft()
        for prereq in prereqs[current]:
            if prereq not in completed and prereq not in needed:
                needed.add(prereq)
                queue.append(prereq)
    result = []
    for course in courses:
        if course in needed:
            result.append(course)
    return result


"""
Function to check the student's ranking before planning

Input : Course preference order list, reverse adjacency list, list of needed courses
Output : None OR error if a needed course is missing / course is ranked before its prereq
"""
def check_rank(rank, prereqs, needed):
    position = {}
    for i, course in enumerate(rank):
        position[course] = i
    for course in needed:
        if course not in position:
            raise ValueError(f"{course} is needed but not ranked")
    for course in rank:
        for prereq in prereqs[course]:
            if prereq in position and position[prereq] > position[course]:
                raise ValueError(f"{course} is ranked before its prerequisite {prereq}")


"""
Function that returns available courses (needed-completed) after every semester

Input : List of courses, reverse adjacency list, set of completed courses
Output : List of courses unlocked (prereqs completed) / available (no prereqs)
"""
def available(courses, prereqs, completed):
    result = []
    for course in courses:
        if course in completed:
            continue
        ready = True
        for prereq in prereqs[course]:
            if prereq not in completed:
                ready = False
                break
        if ready:
            result.append(course)
    return result



"""
Function to schedule semesters until every needed course is completed

Input : Student class instance, max courses per semester, course preference list
Output : List of semesters or error if course before prereq.
"""
def plan_semesters(student, limit, rank):
    check_rank(rank, student.program.prereqs, student.needed)
    position = {}
    for i, course in enumerate(rank):
        position[course] = i 
    while any(course not in student.completed for course in student.needed):
        ordered = sorted(student.available, key=lambda course: position[course]) # ordering available courses according to rank order
        chosen = ordered[:limit] # Takes first k courses from ranked uptill semester limit
        student.semesters.append(chosen)
        student.complete(chosen)               
    return student.semesters
