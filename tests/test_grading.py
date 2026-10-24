"""Module 1: sms.grading (cases from TEST_PLAN.md)."""
import pytest

from sms.grading import calculate_gpa, calculate_grade
from sms.models import Course, Enrollment

pytestmark = pytest.mark.grading


def graded(marks, credits=3):
    return Enrollment(Course("X", "Course", credits), 1, marks)


class TestCalculateGrade:
    @pytest.mark.smoke
    def test_top_band(self):
        assert calculate_grade(90) == ("A", 4.0)

    @pytest.mark.unit
    @pytest.mark.parametrize("marks, letter, points", [
        (92, "A", 4.0), (82, "A-", 3.7), (77, "B+", 3.3), (72, "B", 3.0), (67, "B-", 2.7),
        (62, "C+", 2.3), (57, "C", 2.0), (52, "D", 1.0), (25, "F", 0.0),
    ])
    def test_ecp_one_value_per_band(self, marks, letter, points):
        assert calculate_grade(marks) == (letter, points)

    @pytest.mark.unit
    @pytest.mark.parametrize("marks, letter", [
        (100, "A"), (85, "A"), (84.99, "A-"), (80, "A-"), (79.99, "B+"), (75, "B+"), (74.99, "B"),
        (70, "B"), (69.99, "B-"), (65, "B-"), (64.99, "C+"), (60, "C+"), (59.99, "C"),
        (55, "C"), (54.99, "D"), (50, "D"), (49.99, "F"), (0, "F"),
    ])
    def test_bva_band_edges(self, marks, letter):
        assert calculate_grade(marks)[0] == letter

    @pytest.mark.unit
    def test_int_and_float_agree(self):
        assert calculate_grade(70) == calculate_grade(70.0)

    @pytest.mark.unit
    def test_returns_letter_points_tuple(self):
        letter, points = calculate_grade(65)
        assert isinstance(letter, str) and isinstance(points, float)

    @pytest.mark.negative
    def test_below_zero_returns_none(self):
        # range is enforced by School.enter_marks, not here (TEST_PLAN observation 1)
        assert calculate_grade(-1) is None

    @pytest.mark.negative
    def test_above_hundred_is_not_rejected(self):
        assert calculate_grade(150) == ("A", 4.0)


class TestCalculateGpa:
    @pytest.mark.smoke
    def test_single_course(self):
        assert calculate_gpa([graded(90)]) == 4.0

    @pytest.mark.unit
    def test_empty_is_zero(self):
        assert calculate_gpa([]) == 0.0

    @pytest.mark.unit
    def test_all_ungraded_is_zero(self):
        assert calculate_gpa([graded(None), graded(None, 4)]) == 0.0

    @pytest.mark.unit
    def test_weighted_by_credit_hours(self):
        assert calculate_gpa([graded(90, 3), graded(72, 2)]) == 3.6  # (4*3 + 3*2) / 5

    @pytest.mark.unit
    def test_ungraded_ignored(self):
        assert calculate_gpa([graded(90, 3), graded(None, 4)]) == 4.0

    @pytest.mark.unit
    def test_rounded_to_two_decimals(self):
        assert calculate_gpa([graded(90, 3), graded(40, 4)]) == 1.71  # 12 / 7

    @pytest.mark.unit
    @pytest.mark.parametrize("marks, expected", [([10, 49.99], 0.0), ([85, 100], 4.0)], ids=["all-F", "all-A"])
    def test_bva_min_and_max(self, marks, expected):
        assert calculate_gpa([graded(m) for m in marks]) == expected

    @pytest.mark.unit
    def test_accepts_generator(self):
        assert calculate_gpa(graded(m) for m in [90, 72]) == 3.5
