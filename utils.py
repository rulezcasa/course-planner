"""
Small helper functions used by the planner and the CLI.

Contributor : Suharrsh

Note for instructor : Added appropriate docstrings for logic and explanation
"""

"""
Function to get the term after the given one

Input : Term as "Fall 2026" or "Spring 2027"
Output : Next term ("Fall 2026" -> "Spring 2027", "Spring 2027" -> "Fall 2027")
"""
def next_term(term):
    season, year = term.split()
    if season == "Fall":
        return f"Spring {int(year) + 1}"
    return f"Fall {year}"


"""
Function to find the graduation term

Input : start term, number of planned semesters
Output : Term of the last planned semester, OR None if the plan is empty (already eligible to graduate)
"""
def graduation_term(start_term, num_semesters):
    if num_semesters == 0:
        return None
    term = start_term
    for _ in range(num_semesters - 1):
        term = next_term(term)
    return term


"""
Function to read a comma separated list of course IDs from CLI input

Input : User input
Output : List of course IDs, OR an empty list if the input is blank
"""
def read_list(prompt):
    text = input(prompt)
    if text == "":
        return []
    courses = []
    for course in text.split(","):
        courses.append(course.strip())          # Split and strip on commas
    return courses
