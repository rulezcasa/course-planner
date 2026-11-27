# Course Prerequisite and Graduation Planner

Models a degree program as a directed acyclic graph (DAG) of courses and prerequisites, then builds a semester-by-semester plan to a student's target courses and reports the graduation term.

## Index

- [User flow](#user-flow)
- [Core algorithms and asymptotic runtime](#core-algorithms-and-asymptotic-runtime)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Run](#run)
- [Reproducing a representative test](#reproducing-a-representative-test)
- [Demo video](https://drive.google.com/file/d/10sSacR5DRO4Vm-hcsSPcNDaN_b3QaMCA/view?usp=sharing)
- [Acknowledgments](#acknowledgments)
- [Data Access Statement](#data-access-statement)
- [AI Usage Statement](#ai-usage-statement)
- [Contributions](#contributions)

## User flow

1. **Select a program.**
    - Streamlit: Select a program from the sidebar dropdown.
    - CLI: Pass the course-map file name as an argument:
      ```bash
      python3 main.py se_course_map.json
      ```

2. **Load the program.** The loader builds the prerequisite graph and runs a topological sort (Kahn's algorithm). A program with a cycle or a duplicate is rejected.
    - Streamlit: Click **Load program**. The topological order appears in a green box. If the program is rejected, the courses in the cycle are highlighted in red on the graph.
    - CLI: The program loads as soon as the command runs. It prints every course in topological order, or `Program rejected: ...` and exits.

3. **Enter completed courses.**
    - Streamlit: Pick courses in the **Completed courses** box in the sidebar. They turn green on the graph.
    - CLI: At the `Completed courses` prompt, type the course IDs separated by commas, or press Enter for none:
      ```
      Completed courses (comma separated, blank for none): CMPE 180A
      ```

4. **Enter target courses.**
    - Streamlit: Pick courses in the **Target courses** box in the sidebar.
    - CLI: At the `Target courses` prompt, type the course IDs separated by commas:
      ```
      Target courses (comma separated): CMPE 259, CMPE 295B
      ```

5. **Needed courses are computed.** A backward BFS from the targets finds every prerequisite that isn't completed yet.
    - Streamlit: Needed courses turn yellow on the graph as soon as targets are picked.
    - CLI: The needed list is printed after the start term is entered:
      ```
      Needed courses(including prereqs for target courses): ISE 201, CMPE 252, ...
      ```

6. **Set the semester limit and start term.**
    - Streamlit: Set **Courses per semester**, **Start season** and **Start year** in the sidebar.
    - CLI: Answer the two prompts:
      ```
      Courses per semester: 3
      Start term (e.g. Fall 2026): Fall 2026
      ```

7. **Rank the needed courses.** All needed courses must be ranked, and no course can come before its prerequisite.
    - Streamlit: In the **Rank the needed courses** box, pick the needed courses one by one in order of preference. The first one picked is the highest. Picking a course before its prerequisite shows an error right away, and planning with courses left unranked shows a "needed but not ranked" error.
    - CLI: At the `Rank all needed courses` prompt, type every needed course in order of preference, separated by commas. An invalid ranking prints the reason and asks again:
      ```
      Rank all needed courses (comma separated): ISE 201, CMPE 252, CMPE 257, CMPE 258, CMPE 259, CMPE 294, CMPE 295A, CMPE 295B
      ```

8. **Plan semesters.** Each semester takes up to *k* available courses in ranked order and marks them completed, until every needed course is done.
    - Streamlit: Click **Plan semesters** in the sidebar.
    - CLI: Planning runs right after a valid ranking is entered.

9. **Get the plan.**
    - Streamlit: Shows the number of needed courses, the number of semesters and the graduation term, followed by the colored graph, a slider to step through the semesters and a semester-by-term table.
    - CLI: Prints the plan and the graduation term:
      ```
      Plan:
        Fall 2026: ISE 201
        Spring 2027: CMPE 252, CMPE 257
        ...
      Graduation term: Fall 2028 (5 semesters)
      ```


## Core algorithms and asymptotic runtime

- **Graph construction**: adjacency lists in both directions (`unlocks` and `prereqs`), with validation for duplicate courses, duplicate edges and unknown courses.
- **Topological sort**: Kahn's algorithm. A program whose prerequisites form a cycle is rejected, and the courses in the cycle are reported.
- **Needed courses**: a backward BFS from the target courses over `prereqs` finds every prerequisite the student has not completed yet.
- **Semester planning**: each semester, the planner takes up to *k* of the currently available courses in the student's ranked order and marks them completed. It repeats until every needed course is done.    

| Step | Complexity |
|---|---|
| `build_graph` + `topological_sort` | O(V + E) |
| `needed_courses` | O(V + E) |
| `plan_semesters` | O(S · (V + E)), where S is the number of semesters |

## Project structure

```
course-planner/
├── graph.py          # Graph building and topological_sort logic
├── loader.py         # Reads and validates couse maps and calls graph.py
├── planner.py        # Computes needed courses, rank validation, semester planning
├── utils.py          # Helper functions for term resolution, input reading etc
├── main.py           # CLI
├── benchmark.py      # Test for runtime vs. theoretical complexity
├── demo/
│   ├── app.py        # Streamlit visual demo
│   └── requirements.txt
└── programs/         # Course-map JSON files
    ├── se_course_map.json         # MS Software Engineering (valid)
    ├── cs_course_map.json         # MS Computer Science (valid)
    ├── aerospace_course_map.json  # MS Aerospace (intentional cycle)
    └── ai_course_map.json         # MS AI (intentional duplicate course ID)
```



## Requirements

- **Python 3.8 or newer.** Tested with Python 3.15. The core planner, CLI and benchmark use only the standard library (`json`, `collections`, `random`, `time`, `os`, `sys`).
- **Streamlit 1.30 or newer**, only for the optional visual demo (`demo/requirements.txt`). Streamlit draws the graphs itself, so no separate Graphviz install is needed.

## Run

### 1. CLI
```bash
python3 main.py <course_map_file>
```

`<course_map_file>` is a file name inside `programs/`.


### 2. Streamlit visual demo

```bash
pip install -r demo/requirements.txt
streamlit run demo/app.py
```

The benchmark takes about 10 seconds. It uses a fixed random seed, so the generated graphs are the same on every run.

## Reproducing a representative test

### Test A: plan the MS Computer Science program (4 semesters)

Plan the MS Computer Science program for a student who has finished `CS 42` and `CS 46B` and wants (`CS 257`) and (`CS 265`), taking 3 courses per semester:

```bash
$ python3 main.py cs_course_map.json
...
Student name: Jordan
Completed courses (comma separated, blank for none): CS 42, CS 46B
Target courses (comma separated): CS 257, CS 265
Courses per semester: 3
Start term (e.g. Fall 2026): Fall 2026
Needed courses(including prereqs for target courses): CS 47, CS 146, CS 149, CS 157A, CS 157B, CS 166, CS 257, CS 265
Rank all needed courses (comma separated): CS 146, CS 47, CS 157A, CS 149, CS 166, CS 157B, CS 265, CS 257
```

Expected output :

```
Needed courses(including prereqs for target courses): CS 47, CS 146, CS 149, CS 157A, CS 157B, CS 166, CS 257, CS 265

Plan:
  Fall 2026: CS 146, CS 47
  Spring 2027: CS 157A, CS 149, CS 166
  Fall 2027: CS 157B, CS 265
  Spring 2028: CS 257
Graduation term: Spring 2028 (4 semesters)
```

BFS adds six missing prerequisites to the two targets. In Spring 2027, three courses become available at once and fill the 3-course limit. The plan takes 4 semesters because that is the length of the longest prerequisite chain, `CS 146 → CS 157A → CS 157B → CS 257`.

### Test B: reject invalid programs

```bash
python3 main.py aerospace_course_map.json
# Program rejected, prerequisite cycle among: AE 112, AE 114, AE 119

python3 main.py ai_course_map.json
# Program rejected: Duplicate courseId found in courses: CMPE 297
```

### Test C: invalid ranking is rejected and asked again

Same student, but the first ranking puts `CS 157A` before its prerequisite `CS 146`. The second ranking is valid:

```bash
$ python3 main.py cs_course_map.json
...
Student name: Jordan
Completed courses (comma separated, blank for none): CS 42, CS 46B
Target courses (comma separated): CS 257, CS 265
Courses per semester: 3
Start term (e.g. Fall 2026): Fall 2026

Needed courses(including prereqs for target courses): CS 47, CS 146, CS 149, CS 157A, CS 157B, CS 166, CS 257, CS 265
Rank all needed courses (comma separated): CS 47, CS 157A, CS 146, CS 149, CS 166, CS 157B, CS 265, CS 257
```

Expected output:

```
  CS 157A is ranked before its prerequisite CS 146. Please rank again.
```

### Demo : https://drive.google.com/file/d/10sSacR5DRO4Vm-hcsSPcNDaN_b3QaMCA/view?usp=sharing 

## Acknowledgments
K. Sudheer, H. Thangaraj, S. Subramanyam Venkata contributed to this work while undertaking a project for CS-255 under the guidance of Prof. Ramin Moazeni at San Jose State University.

## Data Access Statement
This project uses the course catalogus publicly available at https://catalog.sjsu.edu/. 

## AI Usage Statement
AI coding tools were used to assist with writing the UI code and generating test cases. The core algorithms, benchmarking, interpretation of results were carried out manually by the team.

## Contributions
All members contributed equally to this project. K. Sudheer built the program loader, graph construction and topological sort (`graph.py`, `loader.py`). H. Thangaraj worked on planning and greedy scheduling, helper functions, project integration (`planner.py`,`utils.py`). S. Subramanyam Venkata implemented CLI, complexity analysis, streamlit demo app and presentation (`main.py`, `demo/app.py`). Data scraping, modelling, unit and functional tests were shared segments.
