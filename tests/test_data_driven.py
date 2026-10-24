"""Data-driven tests: each row of a CSV file in data/ is one test case.
The same cases are listed in test_cases.xlsx.
"""
import csv
from pathlib import Path

import pytest

from sms.grading import calculate_gpa
from sms.models import Course, Enrollment

# path of the data folder inside tests
DATA_FOLDER = Path(__file__).parent / "data"


def read_csv(filename):
    """Read a CSV file and return its rows as a list of dictionaries."""
    rows = []
    with open(DATA_FOLDER / filename, newline="") as file:
        for row in csv.DictReader(file):
            rows.append(row)
    return rows


def get_case_id(row):
    """Name each test after its tc_id column, e.g. TC-DD-01."""
    return row["tc_id"]


# ---------- School.enter_marks, cases from data/enter_marks_cases.csv ----------

@pytest.mark.parametrize("row", read_csv("enter_marks_cases.csv"), ids=get_case_id)
def test_enter_marks(seeded_school, row):
    roll_no = row["roll_no"]
    code = row["code"]
    marks = float(row["marks"])

    if row["expected_error"] == "ValueError":
        with pytest.raises(ValueError):
            seeded_school.enter_marks(roll_no, code, marks)

    elif row["expected_error"] == "KeyError":
        with pytest.raises(KeyError):
            seeded_school.enter_marks(roll_no, code, marks)

    else:
        seeded_school.enter_marks(roll_no, code, marks)
        enrollment = seeded_school.student(roll_no).enrollment(code)
        assert enrollment.grade == row["expected_grade"]
        assert enrollment.grade_points == float(row["expected_points"])


# ---------- calculate_gpa, cases from data/gpa_cases.csv ----------
# "marks" and "credits" hold one value per course, separated by ";"
# a "-" in marks means the marks are not entered yet

@pytest.mark.parametrize("row", read_csv("gpa_cases.csv"), ids=get_case_id)
def test_gpa(row):
    enrollments = []
    if row["marks"] != "":
        marks_list = row["marks"].split(";")
        credits_list = row["credits"].split(";")
        for i in range(len(marks_list)):
            course = Course("X", "Test Course", int(credits_list[i]))
            if marks_list[i] == "-":
                marks = None
            else:
                marks = float(marks_list[i])
            enrollments.append(Enrollment(course, 1, marks))

    assert calculate_gpa(enrollments) == float(row["expected_gpa"])
