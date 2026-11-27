"""
Basic streamlit UI for the demo.

# Contributor : Suharrsh
# AI Usage : AI tools were used to write some parts of this file with full observability by the contributor.

Start command : Run from the project root:  streamlit run demo/app.py
"""

import os
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from graph import CycleError, build_graph                                        # noqa: E402
from loader import load_program, read_program_file                               # noqa: E402
from planner import Student, check_rank, needed_courses, plan_semesters                    # noqa: E402
from utils import graduation_term, next_term                                     # noqa: E402

COMPLETED_COLOR = "#95d5b2"
NEEDED_COLOR = "#fff3b0"


def program_files():
    names = sorted(os.listdir(os.path.join(ROOT, "programs")))
    return [f"programs/{name}" for name in names if name.endswith(".json")]


def to_dot(courses, unlocks, names, fill, show=None):
    """Build a Graphviz DOT string. fill maps course -> color."""
    show = set(courses) if show is None else show
    lines = ["digraph G {", "rankdir=LR;", 'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];']
    for c in courses:
        if c not in show:
            continue
        label = f"{c}\\n{names.get(c, '')[:28]}".replace('"', "'")
        lines.append(f'"{c}" [label="{label}", fillcolor="{fill.get(c, "#eeeeee")}"];')
    for a in courses:
        for b in unlocks[a]:
            if a in show and b in show:
                lines.append(f'"{a}" -> "{b}";')
    lines.append("}")
    return "\n".join(lines)


def show_rejected(path, error):
    st.error(f"Program rejected at load: {error}")
    if isinstance(error, CycleError):
        data, courses, pairs = read_program_file(path)
        unlocks, _ = build_graph(courses, pairs)
        names = {c["course_id"]: c["course_name"] for c in data["courses"]}
        stuck = set(error.cycle_courses)
        fill = {c: ("#ff8fa3" if c in stuck else "#e9ecef") for c in courses}
        st.caption("Red = courses Kahn's algorithm could never order (in-degree never reached 0).")
        st.graphviz_chart(to_dot(courses, unlocks, names, fill), width="stretch")


st.set_page_config(page_title="Course Planner Demo", layout="wide")
st.title("Course Prerequisite and Graduation Planner")

program_name = lambda p: read_program_file(os.path.join(ROOT, p))[0]["name"]
choice = st.sidebar.selectbox("Program", program_files(), index=None, placeholder="Select a program",
                              format_func=program_name)
if choice is None:
    st.info("Select a program in the sidebar to get started.")
    st.stop()

path = os.path.join(ROOT, choice)
data = read_program_file(path)[0]
st.subheader(f"{data['name']} ({data['id']}), {len(data['courses'])} courses")

if st.button("Load program"):
    st.session_state["sorted"] = path            # remembered so results stay shown when other widgets change
if st.session_state.get("sorted") != path:
    st.info("Click Load program to build the prerequisite graph and run the topological sort "
            "(Kahn's algorithm). Programs with a cycle are rejected here.")
    st.stop()

try:
    program = load_program(path)
except (CycleError, ValueError) as error:
    show_rejected(path, error)
    st.stop()

st.success("Topological order:  " + "  ->  ".join(program.order))
label = lambda c: f"{c}  {program.names[c]}"
completed = st.sidebar.multiselect("Completed courses", program.courses, format_func=label)
targets = st.sidebar.multiselect("Target courses", program.courses, format_func=label)
limit = st.sidebar.number_input("Courses per semester", 1, 10, program.semester_limit)
season = st.sidebar.selectbox("Start season", ["Fall", "Spring"])
year = st.sidebar.number_input("Start year", 2024, 2035, 2026)
start_term = f"{season} {year}"


needed = needed_courses(program.courses, program.prereqs, targets, set(completed))
if not targets:
    st.info("Pick target courses in the sidebar.")
    fill = {c: (COMPLETED_COLOR if c in completed else "#eeeeee") for c in program.courses}
    st.graphviz_chart(to_dot(program.courses, program.unlocks, program.names, fill), width="stretch")
    st.stop()

rank = st.sidebar.multiselect("Rank the needed courses (pick them in order of preference, first = highest)",
                              needed, format_func=label)  # multiselect keeps the order courses were picked in
st.sidebar.caption(f"Ranked {len(rank)} of {len(needed)} needed courses.")
try:
    check_rank(rank, program.prereqs, rank)               # live check of the order so far (missing courses checked at planning)
except ValueError as error:
    st.sidebar.error(f"Invalid ranking: {error}")

settings = (path, tuple(completed), tuple(targets), limit, start_term, tuple(rank))
if st.sidebar.button("Plan semesters"):
    st.session_state["planned"] = settings       # any later change to the settings hides the plan again
if st.session_state.get("planned") != settings:
    st.info("Set completed courses, targets, limit and start term, then click Plan semesters in the sidebar.")
    fill = {c: (COMPLETED_COLOR if c in completed else NEEDED_COLOR if c in needed else "#eeeeee") for c in program.courses}
    st.caption("Green = completed, yellow = needed for the targets (found by BFS over prereqs).")
    st.graphviz_chart(to_dot(program.courses, program.unlocks, program.names, fill), width="stretch")
    st.stop()

student = Student("demo", program, completed, targets, needed)
try:
    semesters = plan_semesters(student, limit, rank)
except ValueError as error:
    st.error(f"check_rank rejected this ranking: {error}")
    st.stop()

grad = graduation_term(start_term, len(semesters))
col1, col2, col3 = st.columns(3)
col1.metric("Needed courses", len(needed))
col2.metric("Semesters", len(semesters))
col3.metric("Graduation term", grad or "Already eligible")

step = st.slider("Step through the plan (semesters done)", 0, len(semesters), len(semesters)) if semesters else 0
done = set(completed)
for chosen in semesters[:step]:
    done.update(chosen)

fill = {}
for c in needed:
    fill[c] = "#ffffff" if c in targets else NEEDED_COLOR
for c in done:
    fill[c] = COMPLETED_COLOR
show = set(completed) | set(needed)


def swatch(color, text):
    return (f'<span style="display:inline-block;width:14px;height:14px;background:{color};'
            f'border:2px solid #888;border-radius:3px;vertical-align:middle;margin-right:6px"></span>{text}')


st.markdown("<br>".join([swatch(COMPLETED_COLOR, "Completed"),
                         swatch(NEEDED_COLOR, "Prerequisite"),
                         swatch("#ffffff", "Target")]), unsafe_allow_html=True)
st.graphviz_chart(to_dot(program.courses, program.unlocks, program.names, fill, show),
                  width="stretch")

rows, term = ["| # | Term | Courses |", "|---|---|---|"], start_term     # markdown table, avoids pandas
for i, chosen in enumerate(semesters):
    rows.append(f"| {i + 1} | {term} | {', '.join(chosen)} |")
    term = next_term(term)
st.markdown("\n".join(rows))
