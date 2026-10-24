"""Module 2: sms.models, Enrollment and Student (cases from TEST_PLAN.md)."""
import pytest

from sms.models import Course, Enrollment, Student

CS101 = Course("CS101", "Programming", 3)


@pytest.fixture
def ali(seeded_school):
    return seeded_school.student("CS-001")


@pytest.fixture
def empty_student():
    return Student("CS-002", "Sara Ahmed", "BSCS")


# Enrollment.grade / Enrollment.grade_points

def test_enrollment_graded():
    assert Enrollment(CS101, 1, 90).grade == "A"


@pytest.mark.parametrize("marks, grade, points", [
    (None, None, None), (0, "F", 0.0), (49.99, "F", 0.0), (50, "D", 1.0), (85, "A", 4.0), (100, "A", 4.0),
])
def test_enrollment_grade_and_points(marks, grade, points):
    e = Enrollment(CS101, 1, marks)
    assert (e.grade, e.grade_points) == (grade, points)


def test_enrollment_new_has_no_marks():
    assert Enrollment(CS101, 1).marks is None


def test_enrollment_grade_follows_marks_change():
    e = Enrollment(CS101, 1, 40)
    e.marks = 80
    assert (e.grade, e.grade_points) == ("A-", 3.7)


# Student.enrollment

def test_student_enrollment_returns_enrollment(ali):
    e = ali.enrollment("CS101")
    assert (e.course.code, e.semester, e.marks) == ("CS101", 1, 90)


@pytest.mark.parametrize("code", ["AI201", "cs101", ""], ids=["not-enrolled", "wrong-case", "empty"])
def test_student_enrollment_unknown_code(ali, code):
    with pytest.raises(KeyError):
        ali.enrollment(code)


def test_student_enrollment_with_no_enrollments(empty_student):
    with pytest.raises(KeyError):
        empty_student.enrollment("CS101")


def test_student_enrollment_error_names_student_and_code(ali):
    with pytest.raises(KeyError, match="Ali Khan is not enrolled in AI201"):
        ali.enrollment("AI201")


# Student.semesters

def test_student_semesters_seeded(ali):
    assert ali.semesters() == [1, 2]


def test_student_semesters_no_enrollments(empty_student):
    assert empty_student.semesters() == []


def test_student_semesters_sorted_unique_with_gaps(empty_student):
    for code, sem in [("A", 3), ("B", 1), ("C", 3)]:
        empty_student.enrollments[code] = Enrollment(Course(code, code, 3), sem)
    assert empty_student.semesters() == [1, 3]


# Student.gpa

def test_student_gpa_two_courses(ali):
    assert ali.gpa(["CS101", "MA101"]) == 3.6


@pytest.mark.parametrize("codes, expected", [
    (["CS101"], 4.0), (["CS101", "CS201"], 1.71), ([], 0.0), (["EN101"], 0.0),
], ids=["single", "with-F-rounded", "empty", "ungraded-only"])
def test_student_gpa_subsets(ali, codes, expected):
    assert ali.gpa(codes) == expected


def test_student_gpa_accepts_generator(ali):
    assert ali.gpa(c.strip() for c in " CS101 ,MA101".split(",")) == 3.6


@pytest.mark.parametrize("codes", [["CS101", "AI201"], ["cs101"]], ids=["not-enrolled", "wrong-case"])
def test_student_gpa_unknown_code(ali, codes):
    with pytest.raises(KeyError):
        ali.gpa(codes)


# Student.semester_gpa

def test_student_semester_gpa_semester_one(ali):
    assert ali.semester_gpa(1) == 3.6


def test_student_semester_gpa_fail_and_ungraded(ali):
    assert ali.semester_gpa(2) == 0.0


def test_student_semester_gpa_only_ungraded(seeded_school, ali):
    seeded_school.add_course("AI201", "AI", 3)
    seeded_school.enroll("CS-001", "AI201", 3)
    assert ali.semester_gpa(3) == 0.0


@pytest.mark.parametrize("semester", [0, -1, 3])
def test_student_semester_gpa_semester_without_courses(ali, semester):
    with pytest.raises(KeyError):
        ali.semester_gpa(semester)


# Student.cgpa

def test_student_cgpa_seeded(ali):
    assert ali.cgpa() == 2.0  # 18 / 9


def test_student_cgpa_no_enrollments(empty_student):
    assert empty_student.cgpa() == 0.0


def test_student_cgpa_all_ungraded(empty_student):
    empty_student.enrollments["CS101"] = Enrollment(CS101, 1)
    assert empty_student.cgpa() == 0.0


def test_student_cgpa_changes_after_marks_entered(seeded_school, ali):
    seeded_school.enter_marks("CS-001", "EN101", 90)
    assert ali.cgpa() == 2.36  # 26 / 11
