"""Tests for module 2: sms/models.py, classes Enrollment and Student (see TEST_PLAN.md)."""
import pytest

from sms.models import Course, Enrollment, Student

CS101 = Course("CS101", "Programming", 3)


# student CS-001 from the sample school in conftest.py
@pytest.fixture
def ali(seeded_school):
    return seeded_school.student("CS-001")


# a student with no courses
@pytest.fixture
def new_student():
    return Student("CS-002", "Sara Ahmed", "BSCS")



def test_enrollment_grade_with_marks():
    enrollment = Enrollment(CS101, 1, 90)
    assert enrollment.grade == "A"
    assert enrollment.grade_points == 4.0


def test_enrollment_grade_without_marks_is_none():
    enrollment = Enrollment(CS101, 1)
    assert enrollment.marks is None
    assert enrollment.grade is None
    assert enrollment.grade_points is None

#check that 0 is treated as a real mark not a false
def test_enrollment_zero_marks_is_F_not_none():
    enrollment = Enrollment(CS101, 1, 0)
    assert enrollment.grade == "F"
    assert enrollment.grade_points == 0.0


@pytest.mark.parametrize("marks, grade, points", [
    (49.99, "F", 0.0),
    (50, "D", 1.0),
    (85, "A", 4.0),
    (100, "A", 4.0),
])
def test_enrollment_grade_boundaries(marks, grade, points):
    enrollment = Enrollment(CS101, 1, marks)
    assert enrollment.grade == grade
    assert enrollment.grade_points == points

#check that updating marks reflect
def test_enrollment_grade_changes_when_marks_change():
    enrollment = Enrollment(CS101, 1, 40)
    enrollment.marks = 80
    assert enrollment.grade == "A-"



#student serach function work adn return the righ object 
def test_student_enrollment_found(ali):
    enrollment = ali.enrollment("CS101")
    assert enrollment.course.code == "CS101"
    assert enrollment.semester == 1
    assert enrollment.marks == 90


#test pass when it raise an error
@pytest.mark.parametrize("code", ["AI201", "cs101", ""])
def test_student_enrollment_unknown_code(ali, code):
    with pytest.raises(KeyError):
        ali.enrollment(code)


def test_student_enrollment_student_without_courses(new_student):
    with pytest.raises(KeyError):
        new_student.enrollment("CS101")


def test_student_enrollment_error_message(ali):
    with pytest.raises(KeyError, match="Ali Khan is not enrolled in AI201"):
        ali.enrollment("AI201")



def test_student_semesters(ali):
    assert ali.semesters() == [1, 2]


def test_student_semesters_no_courses(new_student):
    assert new_student.semesters() == []


def test_student_semesters_one_course(school):
    school.add_student("CS-002", "Sara Ahmed", "BSCS")
    school.add_course("CS101", "Programming", 3)
    school.enroll("CS-002", "CS101", 1)
    assert school.student("CS-002").semesters() == [1]


def test_student_semesters_sorted_without_duplicates(school):
    school.add_student("CS-002", "Sara Ahmed", "BSCS")
    school.add_course("A1", "Course A", 3)
    school.add_course("B1", "Course B", 3)
    school.add_course("C1", "Course C", 3)
    school.enroll("CS-002", "A1", 3)
    school.enroll("CS-002", "B1", 1)
    school.enroll("CS-002", "C1", 3)
    assert school.student("CS-002").semesters() == [1, 3]


def test_student_semesters_keeps_gaps(seeded_school, ali):
    seeded_school.add_course("AI201", "Artificial Intelligence", 3)
    seeded_school.enroll("CS-001", "AI201", 4)
    assert ali.semesters() == [1, 2, 4]



def test_student_gpa_two_courses(ali):
    assert ali.gpa(["CS101", "MA101"]) == 3.6


@pytest.mark.parametrize("codes, expected", [
    (["CS101"], 4.0),           
    (["CS101", "CS201"], 1.71), 
    ([], 0.0),                  
    (["EN101"], 0.0),           
])
def test_student_gpa_selected_courses(ali, codes, expected):
    assert ali.gpa(codes) == expected


@pytest.mark.parametrize("codes", [
    ["CS101", "AI201"], 
    ["cs101"],           
])
def test_student_gpa_unknown_code(ali, codes):
    with pytest.raises(KeyError):
        ali.gpa(codes)



def test_student_semester_gpa_semester_1(ali):
    assert ali.semester_gpa(1) == 3.6


def test_student_semester_gpa_with_F_and_no_marks(ali):
    assert ali.semester_gpa(2) == 0.0


def test_student_semester_gpa_only_courses_without_marks(seeded_school, ali):
    seeded_school.add_course("AI201", "Artificial Intelligence", 3)
    seeded_school.enroll("CS-001", "AI201", 3)
    assert ali.semester_gpa(3) == 0.0


@pytest.mark.parametrize("semester", [0, -1, 3])
def test_student_semester_gpa_semester_without_courses(ali, semester):
    with pytest.raises(KeyError):
        ali.semester_gpa(semester)



def test_student_cgpa(ali):
    assert ali.cgpa() == 2.0


def test_student_cgpa_no_courses(new_student):
    assert new_student.cgpa() == 0.0


def test_student_cgpa_no_marks_entered(school):
    school.add_student("CS-002", "Sara Ahmed", "BSCS")
    school.add_course("CS101", "Programming", 3)
    school.enroll("CS-002", "CS101", 1)
    assert school.student("CS-002").cgpa() == 0.0


def test_student_cgpa_after_new_marks(seeded_school, ali):
    seeded_school.enter_marks("CS-001", "EN101", 90)
    assert ali.cgpa() == 2.36


def test_student_cgpa_after_marks_changed(seeded_school, ali):
    seeded_school.enter_marks("CS-001", "CS201", 85)
    assert ali.cgpa() == 3.78
