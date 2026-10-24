"""Fixtures shared by all test files. pytest finds this file by itself.

A fixture is a function that prepares test data. A test asks for it by
using the fixture's name as a parameter, e.g. def test_x(school): ...
Every test gets a fresh copy, so tests cannot affect each other.
"""
import pytest

from sms.school import School


# an empty school
@pytest.fixture
def school():
    return School()


# a school with sample data:
#   student CS-001 (Ali Khan)
#   semester 1: CS101 marks 90 (A, 3 credits), MA101 marks 72 (B, 2 credits)
#   semester 2: CS201 marks 49 (F, 4 credits), EN101 no marks yet (2 credits)
@pytest.fixture
def seeded_school():
    school = School()
    school.add_course("CS101", "Programming", 3)
    school.add_course("MA101", "Calculus", 2)
    school.add_course("CS201", "Data Structures", 4)
    school.add_course("EN101", "English", 2)

    school.add_student("CS-001", "Ali Khan", "BSCS")

    school.enroll("CS-001", "CS101", 1)
    school.enroll("CS-001", "MA101", 1)
    school.enroll("CS-001", "CS201", 2)
    school.enroll("CS-001", "EN101", 2)

    school.enter_marks("CS-001", "CS101", 90)
    school.enter_marks("CS-001", "MA101", 72)
    school.enter_marks("CS-001", "CS201", 49)
    return school
