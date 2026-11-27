"""
Command line interface for the course planner. Entry point:  python3 main.py se_course_map.json  (programs/)

Contributor : Suharrsh

Note for instructor : Added appropriate docstrings for logic and explanation

"""

import os
import sys

from graph import CycleError
from loader import load_program
from planner import Student, needed_courses, plan_semesters
from utils import graduation_term, next_term, read_list


'''
Function to print the semester plan
Input : Number of semesters, start semester
Output : Semester plan and graduation term printed
'''
def print_plan(semesters, start):
    finish = graduation_term(start, len(semesters))
    if finish is None:
        print("\nAll target courses are completed. Already eligible to graduate.")
        return
    print("\nPlan:")
    term = start
    for semester in semesters:
        print(f"  {term}: {', '.join(semester)}")
        term = next_term(term)
    print(f"Graduation term: {finish} ({len(semesters)} semesters)")


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "programs", sys.argv[1])
    try:
        program = load_program(path)
    except CycleError as error: # Cycle error returned by load_program
        print(f"Program rejected, prerequisite cycle among: {', '.join(error.cycle_courses)}")
        sys.exit(1)
    except ValueError as error: # Duplicate courses/ any other error returned by load_program
        print(f"Program rejected: {error}")
        sys.exit(1)

    # Prints all course catalogue
    print(f"{program.name} ({program.id}), {len(program.courses)} courses")
    print("\nCourses in order:")
    for course in program.order:
        print(f"  {course}  {program.names[course]}")

    #User inputs
    name = input("\nStudent name: ")
    completed = read_list("Completed courses (comma separated, blank for none): ")
    targets = read_list("Target courses (comma separated): ")
    needed = needed_courses(program.courses, program.prereqs, targets, completed)
    student = Student(name, program, completed, targets, needed)
    limit = int(input("Courses per semester: "))
    start = input("Start term (e.g. Fall 2026): ")

    # Prints needed coureses based on target + its prereqs
    print(f"\nNeeded courses(including prereqs for target courses): {', '.join(needed)}")
    while True:
        rank = read_list("Rank all needed courses (comma separated): ")
        try:
            semesters = plan_semesters(student, limit, rank)
            break
        except ValueError as error:
            print(f"  {error}. Please rank again.")      # Prereq error returned by check_rank
    print_plan(semesters, start)


if __name__ == "__main__":
    main()
