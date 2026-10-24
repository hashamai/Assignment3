"""Module 1: sms.grading (cases from TEST_PLAN.md)."""
import pytest

from sms.grading import calculate_gpa, calculate_grade
from sms.models import Course, Enrollment


def graded(marks, credits=3):
    return Enrollment(Course("X", "Course", credits), 1, marks)


# calculate_grade

def test_calculate_grade_top_band():
    assert calculate_grade(90) == ("A", 4.0)


@pytest.mark.parametrize("marks, letter, points", [
    (92, "A", 4.0), (82, "A-", 3.7), (77, "B+", 3.3), (72, "B", 3.0), (67, "B-", 2.7),
    (62, "C+", 2.3), (57, "C", 2.0), (52, "D", 1.0), (25, "F", 0.0),
])
def test_calculate_grade_ecp_one_value_per_band(marks, letter, points):
    assert calculate_grade(marks) == (letter, points)


@pytest.mark.parametrize("marks, letter", [
    (100, "A"), (85, "A"), (84.99, "A-"), (80, "A-"), (79.99, "B+"), (75, "B+"), (74.99, "B"),
    (70, "B"), (69.99, "B-"), (65, "B-"), (64.99, "C+"), (60, "C+"), (59.99, "C"),
    (55, "C"), (54.99, "D"), (50, "D"), (49.99, "F"), (0, "F"),
])
def test_calculate_grade_bva_band_edges(marks, letter):
    assert calculate_grade(marks)[0] == letter


def test_calculate_grade_int_and_float_agree():
    assert calculate_grade(70) == calculate_grade(70.0)


def test_calculate_grade_returns_letter_points_tuple():
    letter, points = calculate_grade(65)
    assert isinstance(letter, str) and isinstance(points, float)


def test_calculate_grade_below_zero_returns_none():
    # range is enforced by School.enter_marks, not here (TEST_PLAN observation 1)
    assert calculate_grade(-1) is None


def test_calculate_grade_above_hundred_is_not_rejected():
    assert calculate_grade(150) == ("A", 4.0)


# calculate_gpa

def test_calculate_gpa_single_course():
    assert calculate_gpa([graded(90)]) == 4.0


def test_calculate_gpa_empty_is_zero():
    assert calculate_gpa([]) == 0.0


def test_calculate_gpa_all_ungraded_is_zero():
    assert calculate_gpa([graded(None), graded(None, 4)]) == 0.0


def test_calculate_gpa_weighted_by_credit_hours():
    assert calculate_gpa([graded(90, 3), graded(72, 2)]) == 3.6  # (4*3 + 3*2) / 5


def test_calculate_gpa_ungraded_ignored():
    assert calculate_gpa([graded(90, 3), graded(None, 4)]) == 4.0


def test_calculate_gpa_rounded_to_two_decimals():
    assert calculate_gpa([graded(90, 3), graded(40, 4)]) == 1.71  # 12 / 7


@pytest.mark.parametrize("marks, expected", [([10, 49.99], 0.0), ([85, 100], 4.0)], ids=["all-F", "all-A"])
def test_calculate_gpa_bva_min_and_max(marks, expected):
    assert calculate_gpa([graded(m) for m in marks]) == expected


def test_calculate_gpa_accepts_generator():
    assert calculate_gpa(graded(m) for m in [90, 72]) == 3.5
