"""Tests for module 3: sms/school.py, class School (see TEST_PLAN.md)."""
import pytest


@pytest.fixture
def school_with_ai(seeded_school):
    seeded_school.add_course("AI201", "Artificial Intelligence", 3)
    return seeded_school



@pytest.mark.smoke
@pytest.mark.order(9)
def test_add_student(school):
    school.add_student("CS-001", "Ali Khan", "BSCS")
    student = school.student("CS-001")
    assert student.roll_no == "CS-001"
    assert student.name == "Ali Khan"
    assert student.program == "BSCS"
    assert student.enrollments == {}


def test_add_student_one_character_fields(school):
    school.add_student("1", "A", "B")
    assert "1" in school.students


def test_add_student_empty_program_is_accepted(school):
    # program is not checked (TEST_PLAN observation 3)
    school.add_student("CS-001", "Ali Khan", "")
    assert school.student("CS-001").program == ""


def test_add_student_roll_no_is_case_sensitive(school):
    school.add_student("CS-001", "Ali Khan", "BSCS")
    school.add_student("cs-001", "Other Student", "BSCS")
    assert len(school.students) == 2


@pytest.mark.parametrize("roll_no, name", [
    ("", "Ali"),      
    ("CS-001", ""),   
    (None, "Ali"),    
    ("CS-001", None), 
])
@pytest.mark.negative
def test_add_student_missing_roll_no_or_name(school, roll_no, name):
    with pytest.raises(ValueError):
        school.add_student(roll_no, name, "BSCS")
    assert school.students == {}


@pytest.mark.negative
def test_add_student_duplicate_roll_no(seeded_school):
    with pytest.raises(ValueError):
        seeded_school.add_student("CS-001", "Someone Else", "BSSE")
    # the first student is not replaced
    assert seeded_school.student("CS-001").name == "Ali Khan"



@pytest.mark.smoke
@pytest.mark.order(10)
def test_add_course(school):
    school.add_course("CS101", "Programming", 3)
    course = school.course("CS101")
    assert course.code == "CS101"
    assert course.title == "Programming"
    assert course.credit_hours == 3


@pytest.mark.parametrize("credit_hours", [1, 6])
def test_add_course_valid_credit_hours(school, credit_hours):
    school.add_course("CS101", "Programming", credit_hours)
    assert school.course("CS101").credit_hours == credit_hours


@pytest.mark.parametrize("credit_hours", [0, -1])
@pytest.mark.negative
def test_add_course_invalid_credit_hours(school, credit_hours):
    with pytest.raises(ValueError):
        school.add_course("CS101", "Programming", credit_hours)
    assert school.courses == {}


@pytest.mark.parametrize("code, title", [
    ("", "Programming"),  # empty code
    ("CS101", ""),        # empty title
])
@pytest.mark.negative
def test_add_course_missing_code_or_title(school, code, title):
    with pytest.raises(ValueError):
        school.add_course(code, title, 3)


@pytest.mark.negative
def test_add_course_duplicate_code(seeded_school):
    with pytest.raises(ValueError):
        seeded_school.add_course("CS101", "Other Course", 1)
    # the first course is not replaced
    assert seeded_school.course("CS101").title == "Programming"



@pytest.mark.smoke
@pytest.mark.order(11)
def test_enroll(school_with_ai):
    school_with_ai.enroll("CS-001", "AI201", 3)
    enrollment = school_with_ai.student("CS-001").enrollment("AI201")
    assert enrollment.course.code == "AI201"
    assert enrollment.semester == 3
    assert enrollment.marks is None


@pytest.mark.parametrize("semester", [1, 8])
def test_enroll_valid_semester(school_with_ai, semester):
    school_with_ai.enroll("CS-001", "AI201", semester)
    assert school_with_ai.student("CS-001").enrollment("AI201").semester == semester


@pytest.mark.parametrize("semester", [0, -1])
@pytest.mark.negative
def test_enroll_invalid_semester(school_with_ai, semester):
    with pytest.raises(ValueError):
        school_with_ai.enroll("CS-001", "AI201", semester)
    assert "AI201" not in school_with_ai.student("CS-001").enrollments


@pytest.mark.negative
def test_enroll_unknown_student(school_with_ai):
    with pytest.raises(KeyError):
        school_with_ai.enroll("CS-999", "AI201", 1)


@pytest.mark.negative
def test_enroll_unknown_course(school_with_ai):
    with pytest.raises(KeyError):
        school_with_ai.enroll("CS-001", "XX999", 1)


@pytest.mark.negative
def test_enroll_already_enrolled(seeded_school):
    with pytest.raises(ValueError):
        seeded_school.enroll("CS-001", "CS101", 2)
    assert seeded_school.student("CS-001").enrollment("CS101").semester == 1



@pytest.mark.smoke
@pytest.mark.order(12)
def test_enter_marks(seeded_school):
    seeded_school.enter_marks("CS-001", "EN101", 81)
    assert seeded_school.student("CS-001").enrollment("EN101").marks == 81


@pytest.mark.parametrize("marks", [0, 0.01, 50, 99.99, 100])
def test_enter_marks_valid(seeded_school, marks):
    seeded_school.enter_marks("CS-001", "EN101", marks)
    assert seeded_school.student("CS-001").enrollment("EN101").marks == marks


def test_enter_marks_again_replaces_old_marks(seeded_school):
    seeded_school.enter_marks("CS-001", "CS101", 55)
    assert seeded_school.student("CS-001").enrollment("CS101").marks == 55


@pytest.mark.parametrize("marks", [-1, -0.01, 100.01, 101])
@pytest.mark.negative
def test_enter_marks_invalid(seeded_school, marks):
    with pytest.raises(ValueError):
        seeded_school.enter_marks("CS-001", "CS101", marks)
    # the old marks are kept
    assert seeded_school.student("CS-001").enrollment("CS101").marks == 90


@pytest.mark.negative
def test_enter_marks_unknown_student(seeded_school):
    with pytest.raises(KeyError):
        seeded_school.enter_marks("CS-999", "CS101", 70)


@pytest.mark.negative
def test_enter_marks_course_not_enrolled(seeded_school):
    with pytest.raises(KeyError):
        seeded_school.enter_marks("CS-001", "AI201", 70)


@pytest.mark.negative
def test_enter_marks_range_is_checked_first(seeded_school):
    with pytest.raises(ValueError):
        seeded_school.enter_marks("CS-999", "CS101", 101)



@pytest.mark.smoke
@pytest.mark.order(13)
def test_student_lookup(seeded_school):
    assert seeded_school.student("CS-001").name == "Ali Khan"


def test_student_lookup_new_student(school):
    school.add_student("CS-002", "Sara Ahmed", "BSCS")
    assert school.student("CS-002").name == "Sara Ahmed"


@pytest.mark.smoke
@pytest.mark.order(14)
def test_course_lookup(seeded_school):
    assert seeded_school.course("CS101").title == "Programming"


def test_course_lookup_new_course(school):
    school.add_course("AI201", "Artificial Intelligence", 3)
    assert school.course("AI201").credit_hours == 3


@pytest.mark.parametrize("roll_no", ["CS-999", "cs-001", ""])
@pytest.mark.negative
def test_student_lookup_not_found(seeded_school, roll_no):
    with pytest.raises(KeyError):
        seeded_school.student(roll_no)


@pytest.mark.parametrize("code", ["XX999", "cs101", ""])
@pytest.mark.negative
def test_course_lookup_not_found(seeded_school, code):
    with pytest.raises(KeyError):
        seeded_school.course(code)
