"""Tests for module 1: sms/grading.py (see TEST_PLAN.md)."""
import pytest

from sms.grading import calculate_gpa, calculate_grade
from sms.models import Course, Enrollment


def make_enrollment(marks, credits=3):
    """Helper: an enrollment in a test course with the given marks and credit hours."""
    course = Course("X", "Test Course", credits)
    return Enrollment(course, 1, marks)


# ---------- calculate_grade ----------

def test_calculate_grade_90_is_A():
    assert calculate_grade(90) == ("A", 4.0)


# ECP: one value from inside each grade band
@pytest.mark.parametrize("marks, letter, points", [
    (92, "A", 4.0),
    (82, "A-", 3.7),
    (77, "B+", 3.3),
    (72, "B", 3.0),
    (67, "B-", 2.7),
    (62, "C+", 2.3),
    (57, "C", 2.0),
    (52, "D", 1.0),
    (25, "F", 0.0),
])
def test_calculate_grade_each_band(marks, letter, points):
    assert calculate_grade(marks) == (letter, points)


# BVA: the lowest marks of each band, and the marks just below it
@pytest.mark.parametrize("marks, expected_letter", [
    (100, "A"),
    (85, "A"), (84.99, "A-"),
    (80, "A-"), (79.99, "B+"),
    (75, "B+"), (74.99, "B"),
    (70, "B"), (69.99, "B-"),
    (65, "B-"), (64.99, "C+"),
    (60, "C+"), (59.99, "C"),
    (55, "C"), (54.99, "D"),
    (50, "D"), (49.99, "F"),
    (0, "F"),
])
def test_calculate_grade_boundaries(marks, expected_letter):
    letter, points = calculate_grade(marks)
    assert letter == expected_letter


def test_calculate_grade_int_and_float_give_same_result():
    assert calculate_grade(70) == calculate_grade(70.0)


def test_calculate_grade_below_zero_returns_none():
    # calculate_grade does not check the range; School.enter_marks does (TEST_PLAN observation 1)
    assert calculate_grade(-1) is None


def test_calculate_grade_above_100_still_gives_A():
    assert calculate_grade(150) == ("A", 4.0)


# ---------- calculate_gpa ----------

def test_calculate_gpa_one_course():
    assert calculate_gpa([make_enrollment(90)]) == 4.0


def test_calculate_gpa_no_courses_is_zero():
    assert calculate_gpa([]) == 0.0


def test_calculate_gpa_no_marks_entered_is_zero():
    enrollments = [make_enrollment(None), make_enrollment(None, credits=4)]
    assert calculate_gpa(enrollments) == 0.0


def test_calculate_gpa_weighted_by_credit_hours():
    # (4.0 * 3 + 3.0 * 2) / 5 = 3.6
    enrollments = [make_enrollment(90, credits=3), make_enrollment(72, credits=2)]
    assert calculate_gpa(enrollments) == 3.6


def test_calculate_gpa_ignores_course_without_marks():
    enrollments = [make_enrollment(90, credits=3), make_enrollment(None, credits=4)]
    assert calculate_gpa(enrollments) == 4.0


def test_calculate_gpa_rounds_to_two_decimals():
    # (4.0 * 3 + 0.0 * 4) / 7 = 1.714...
    enrollments = [make_enrollment(90, credits=3), make_enrollment(40, credits=4)]
    assert calculate_gpa(enrollments) == 1.71


def test_calculate_gpa_all_F_is_lowest():
    enrollments = [make_enrollment(10), make_enrollment(49.99)]
    assert calculate_gpa(enrollments) == 0.0


def test_calculate_gpa_all_A_is_highest():
    enrollments = [make_enrollment(85), make_enrollment(100)]
    assert calculate_gpa(enrollments) == 4.0
