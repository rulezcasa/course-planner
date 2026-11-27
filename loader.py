"""
Loading and processing of program course maps 

Contributor : Keerthana 

Note for instructor : Added appropriate docstrings for logic and explanation
"""


import json
from graph import build_graph, topological_sort # Custom built functions from graph.py

"""
Custom class holding program metadata
"""
class Program:
    def __init__(self, name, program_id, courses, names, unlocks, prereqs, order, semester_limit):
        self.name = name                        # Program name
        self.id = program_id                    # Program ID
        self.courses = courses                  # List of course IDs 
        self.names = names                      # Course ID -> Course name
        self.unlocks = unlocks                  # Forward adjacency list from build_graph()
        self.prereqs = prereqs                  # Reverse adjacency list from build_graph()
        self.order = order                      # Topological order
        self.semester_limit = semester_limit    # Maximum courses per semester


"""
Function to read raw json files 

Input : File path
Output : 
    1. data: Raw json data used by load_program below
    2. courses : List of courses (unordered)
    3. pairs : List of pairs ([A,B] denotes A comes before B)
"""
def read_program_file(path):
    """Return (data, courses, pairs) from a course-map JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    courses = [c["course_id"] for c in data["courses"]]
    pairs = [[p, c["course_id"]] for c in data["courses"] for p in c["prereqs"]]
    return data, courses, pairs


"""
Function to load program and validate

Input : File path, Semester limit as integer
Output : Program class OR error if cycle/duplicate pair/missing pair

"""
def load_program(path, semester_limit=None):
    data, courses, pairs = read_program_file(path)      
    unlocks, prereqs = build_graph(courses, pairs)              # Adjacency lists
    order = topological_sort(courses, unlocks)                  # Topological ordered list
    limit = semester_limit or data.get("semester_limit", 3) 
    names = {c["course_id"]: c["course_name"] for c in data["courses"]}
    return Program(data["name"], data["id"], courses, names, unlocks, prereqs, order, limit)

