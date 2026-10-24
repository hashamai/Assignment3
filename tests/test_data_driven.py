"""Data-driven cases read from data/*.csv; the same cases are listed in test_cases.xlsx."""
import csv
from pathlib import Path

import pytest

from sms.grading import calculate_gpa
from sms.models import Course, Enrollment

pytestmark = pytest.mark.data_driven

DATA = Path(__file__).parent / "data"
ERRORS = {"ValueError": ValueError, "KeyError": KeyError}


def cases(filename):
    with open(DATA / filename, newline="") as f:
        return [pytest.param(row, id=row["tc_id"]) for row in csv.DictReader(f)]


@pytest.mark.school
@pytest.mark.parametrize("row", cases("enter_marks_cases.csv"))
def test_enter_marks(seeded_school, row):
    args = row["roll_no"], row["code"], float(row["marks"])
    if row["expected_error"]:
        with pytest.raises(ERRORS[row["expected_error"]]):
            seeded_school.enter_marks(*args)
    else:
        seeded_school.enter_marks(*args)
        e = seeded_school.student(row["roll_no"]).enrollment(row["code"])
        assert (e.grade, e.grade_points) == (row["expected_grade"], float(row["expected_points"]))


@pytest.mark.grading
@pytest.mark.parametrize("row", cases("gpa_cases.csv"))
def test_gpa(row):
    # "marks" and "credits" are ";"-separated lists of equal length; "-" means marks not entered
    marks, credits = row["marks"].split(";"), row["credits"].split(";")
    enrollments = [Enrollment(Course(f"C{i}", "Course", int(c)), 1, None if m == "-" else float(m))
                   for i, (m, c) in enumerate(zip(marks, credits)) if c]
    assert calculate_gpa(enrollments) == float(row["expected_gpa"])
