"""Shared fixtures."""
import pytest

from sms.school import School


@pytest.fixture
def school():
    return School()


@pytest.fixture
def seeded_school():
    """Student CS-001 with CS101 90 (A, 3 cr), MA101 72 (B, 2 cr) in semester 1,
    CS201 49 (F, 4 cr) and EN101 ungraded (2 cr) in semester 2."""
    school = School()
    for code, title, credits in [("CS101", "Programming", 3), ("MA101", "Calculus", 2),
                                 ("CS201", "Data Structures", 4), ("EN101", "English", 2)]:
        school.add_course(code, title, credits)
    school.add_student("CS-001", "Ali Khan", "BSCS")
    for code, semester, marks in [("CS101", 1, 90), ("MA101", 1, 72), ("CS201", 2, 49), ("EN101", 2, None)]:
        school.enroll("CS-001", code, semester)
        if marks is not None:
            school.enter_marks("CS-001", code, marks)
    return school
