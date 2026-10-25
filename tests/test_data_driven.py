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



@pytest.mark.parametrize("row", read_csv("enter_marks_cases.csv"), ids=get_case_id)
def test_enter_marks(seeded_school, row):
    roll_no = row["roll_no"]
    code = row["course_code"]
    marks = float(row["marks"])
    expected = row["expected"]  # a grade such as "A", or the error the code must raise

    if expected == "ValueError":
        with pytest.raises(ValueError):
            seeded_school.enter_marks(roll_no, code, marks)

    elif expected == "KeyError":
        with pytest.raises(KeyError):
            seeded_school.enter_marks(roll_no, code, marks)

    else:
        seeded_school.enter_marks(roll_no, code, marks)
        enrollment = seeded_school.student(roll_no).enrollment(code)
        assert enrollment.grade == expected


def read_marks(text):
    """'none' in the CSV means the marks are not entered yet."""
    if text == "none":
        return None
    return float(text)


@pytest.mark.parametrize("row", read_csv("gpa_cases.csv"), ids=get_case_id)
def test_gpa(row):
    course_1 = Course("C1", "Course 1", int(row["credits_1"]))
    course_2 = Course("C2", "Course 2", int(row["credits_2"]))
    enrollment_1 = Enrollment(course_1, 1, read_marks(row["marks_1"]))
    enrollment_2 = Enrollment(course_2, 1, read_marks(row["marks_2"]))

    assert calculate_gpa([enrollment_1, enrollment_2]) == float(row["expected_gpa"])
