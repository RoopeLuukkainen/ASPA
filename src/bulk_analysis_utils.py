import pathlib
import json
import copy
import re
from collections import Counter

import src.config.templates as templates


METADATA_FILENAME = "metadata.json"
USER_FIELD = "user"
STUDENT_NUMBER_FIELD = "username"
NAME_FIELD = "name"
CG_ID_FIELD = "id"
# ASSIGNMENT_ID_FIELD = "assignment_id"
ASSIGNMENTS_FIELD = "assignments"

ASSIGNMENT_PATT = r".*(?P<assignment_name>L\d+T\d)+.*"
LIB_FILE_NAME = "Kirjasto"
LIB_PATT = rf"(?P<before>.*){LIB_FILE_NAME}(?P<after>.*)"

# SPECIAL_ASSIGNMENT_NAMES = {
#     "HTMinimi": "HTMinimitaso",
#     "HTPerus": "HTPerustaso",
#     "HTTavoite": "HTTavoitetaso"
# }

# ---------------------------------------------------------------------------- #
# Classes

class Student:
    def __init__(self, student_number:str, name: str, codegrade_id: str):
        self._student_number = student_number
        self._name = name
        self._codegrade_id = codegrade_id
        self.assignments = {}

    @property
    def student_number(self):
        return self._student_number

    @property
    def name(self):
        return self._name

    @property
    def codegrade_id(self):
        return self._codegrade_id

    def get_assignments(self):
        return self.assignments

    def add_assignment(self, assignment_id, assignment_obj):
        self.assignments[assignment_id] = assignment_obj

class Assignment:
    def __init__(self, assignment_name, filepath):
        self._assignment_name = assignment_name
        self._filepaths = [filepath]
        self.violations = Counter()
        self.feedback = None

    @property
    def assignment_name(self):
        return self._assignment_name

    def get_violations(self, return_copy=False):
        if return_copy:
            return copy.deepcopy(self.violations)
        return self.violations

    def update_violations(self, new_violations):
        self.violations.update(new_violations)

    def get_feedback(self):
        return self.feedback

    def set_feedback(self, feedback_str):
        self.feedback = feedback_str

    def append_feedback(self, feedback_str):
        if self.feedback:
            self.feedback += feedback_str
        else:
            self.set_feedback(feedback_str)

    def get_filepaths(self):
        return self._filepaths

    def add_filepath(self, filepath):
        self._filepaths.append(filepath)

# ---------------------------------------------------------------------------- #
# Parsing data

def parse_metadata(metadata_path, student_dict):
    try:
        with open(metadata_path, mode="r", encoding="UTF-8") as fhandle:
            data = json.load(fhandle)
    except OSError as err:
        print(f"Error while opening a file at path '{metadata_path}'\n{err}")

    user_info = data[USER_FIELD]
    student_dict[user_info[STUDENT_NUMBER_FIELD]] = Student(
        user_info[STUDENT_NUMBER_FIELD],
        user_info[NAME_FIELD],
        user_info[CG_ID_FIELD]
    )

    return user_info[STUDENT_NUMBER_FIELD]

def parse_students_and_filepaths(root: pathlib.Path) -> dict:
    """Expects each student being in different directory starting from root."""

    if not root.is_dir():
        print(f"Invalid filepath for bulkanalysis '{root}' is not a directory. Give path to root directory.")
        return {}

    assignment_patt = re.compile(ASSIGNMENT_PATT)
    lib_patt = re.compile(LIB_PATT)
    student_dict = {}
    for student_dir in root.iterdir():
        # Find metadata only once
        metadata_path = None
        for path in student_dir.glob(f"**/{METADATA_FILENAME}"):
            metadata_path = path
            break
        else:
            print(f"No metadata file '{METADATA_FILENAME}' found in directory tree starting from '{student_dir}'.")
            continue

        student_id = parse_metadata(metadata_path, student_dict)

        # Get python file paths
        temp_assignment_dict = {}
        for path in student_dir.glob("**/*.py"):
            # Normally named weekly assignments
            if (match := assignment_patt.match(path.stem)):
                assignment_name = match.group("assignment_name")
                # print("0", assignment_name)

            # Normally named course project's libarary file
            elif (LIB_FILE_NAME in path.stem
                and (match := lib_patt.match(path.stem))):

                assignment_name = "".join([match.group("before"), match.group("after")])
                # print("1", assignment_name)

            else:
                assignment_name = path.stem
                # print("2", assignment_name)


            filepath_template_obj = templates.FilepathTemplate(
                path=path,
                student=student_id,
                course=root.stem  # Name of root directory
            )

            if (temp := temp_assignment_dict.setdefault(assignment_name)):
                temp.add_filepath(filepath_template_obj)
            else:
                temp_assignment_dict[assignment_name] = Assignment(
                    assignment_name,
                    filepath_template_obj
                )

        # Add assignments to students
        for assignment_name, assignment_obj in temp_assignment_dict.items():
            student_dict[student_id].add_assignment(assignment_name, assignment_obj)

    return student_dict


# ---------------------------------------------------------------------------- #
# Writing

def write_results(json_path, student_dict, root_dir_name):

    # Loop students and add them metadata and init assignments dict
    temp = {}
    for student, student_obj in student_dict.items():
        student_data = temp.setdefault(
            student, {
                # If new student add name, id, studentnumber
                "name": student_obj.name,
                "codegrade_id": student_obj.codegrade_id,
                "student_number": student_obj.student_number,
                "assignments": {}
            }
        )

        # Loop assignments and add violation counters to assignment
        for assignment_id, assignment_obj in student_obj.get_assignments().items():
            violations_dict = assignment_obj.get_violations(return_copy=True)
            student_data["assignments"].setdefault(assignment_id, Counter()).update(violations_dict)

    to_json_data = {root_dir_name: temp}
    write_json(json_path, to_json_data)


def write_json(json_path, json_data):
    try:
        with open(json_path, mode="w", encoding="UTF-8") as fhandle:
            json.dump(json_data, fhandle, ensure_ascii=False, indent=4)
    except OSError as err:
        print(f"Error while opening a file at path '{json_path}'\n{err}")

