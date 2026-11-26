"""Load a program JSON file (course map format) into courses + pairs."""

import json

from graph import build_graph, topological_sort


class Program:
    def __init__(self, name, program_id, courses, names, unlocks, prereqs, order,
                 semester_limit):
        self.name = name
        self.id = program_id
        self.courses = courses          # list of course IDs, file order
        self.names = names              # course ID -> course name
        self.unlocks = unlocks
        self.prereqs = prereqs
        self.order = order              # topological order
        self.semester_limit = semester_limit


def read_program_file(path):
    """Return (data, courses, pairs) from a course-map JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    courses = [c["course_id"] for c in data["courses"]]
    pairs = [[p, c["course_id"]] for c in data["courses"] for p in c["prereqs"]]
    return data, courses, pairs


def load_program(path, semester_limit=None):
    """Read the file, build the graph and sort it.

    Raises ValueError for bad data and CycleError for cyclic programs,
    so invalid programs are rejected at load.
    """
    data, courses, pairs = read_program_file(path)
    unlocks, prereqs = build_graph(courses, pairs)
    order = topological_sort(courses, unlocks, prereqs)
    limit = semester_limit or data.get("semester_limit", 3)
    names = {c["course_id"]: c["course_name"] for c in data["courses"]}
    return Program(data["name"], data["id"], courses, names, unlocks, prereqs,
                   order, limit)
