"""Module 2: sms.models, Enrollment and Student (cases from TEST_PLAN.md)."""
import pytest

from sms.models import Course, Enrollment, Student

pytestmark = pytest.mark.models

CS101 = Course("CS101", "Programming", 3)


@pytest.fixture
def ali(seeded_school):
    return seeded_school.student("CS-001")


@pytest.fixture
def empty_student():
    return Student("CS-002", "Sara Ahmed", "BSCS")


class TestEnrollmentGrade:
    @pytest.mark.smoke
    def test_graded(self):
        assert Enrollment(CS101, 1, 90).grade == "A"

    @pytest.mark.unit
    @pytest.mark.parametrize("marks, grade, points", [
        (None, None, None), (0, "F", 0.0), (49.99, "F", 0.0), (50, "D", 1.0), (85, "A", 4.0), (100, "A", 4.0),
    ])
    def test_grade_and_points(self, marks, grade, points):
        e = Enrollment(CS101, 1, marks)
        assert (e.grade, e.grade_points) == (grade, points)

    @pytest.mark.unit
    def test_new_enrollment_has_no_marks(self):
        assert Enrollment(CS101, 1).marks is None

    @pytest.mark.unit
    def test_grade_follows_marks_change(self):
        e = Enrollment(CS101, 1, 40)
        e.marks = 80
        assert (e.grade, e.grade_points) == ("A-", 3.7)


class TestStudentEnrollment:
    @pytest.mark.smoke
    def test_returns_enrollment(self, ali):
        e = ali.enrollment("CS101")
        assert (e.course.code, e.semester, e.marks) == ("CS101", 1, 90)

    @pytest.mark.negative
    @pytest.mark.parametrize("code", ["AI201", "cs101", ""], ids=["not-enrolled", "wrong-case", "empty"])
    def test_unknown_code(self, ali, code):
        with pytest.raises(KeyError):
            ali.enrollment(code)

    @pytest.mark.negative
    def test_student_with_no_enrollments(self, empty_student):
        with pytest.raises(KeyError):
            empty_student.enrollment("CS101")

    @pytest.mark.negative
    def test_error_names_student_and_code(self, ali):
        with pytest.raises(KeyError, match="Ali Khan is not enrolled in AI201"):
            ali.enrollment("AI201")


class TestStudentSemesters:
    @pytest.mark.smoke
    def test_seeded(self, ali):
        assert ali.semesters() == [1, 2]

    @pytest.mark.unit
    def test_no_enrollments(self, empty_student):
        assert empty_student.semesters() == []

    @pytest.mark.unit
    def test_sorted_unique_with_gaps(self, empty_student):
        for code, sem in [("A", 3), ("B", 1), ("C", 3)]:
            empty_student.enrollments[code] = Enrollment(Course(code, code, 3), sem)
        assert empty_student.semesters() == [1, 3]


class TestStudentGpa:
    @pytest.mark.smoke
    def test_two_courses(self, ali):
        assert ali.gpa(["CS101", "MA101"]) == 3.6

    @pytest.mark.unit
    @pytest.mark.parametrize("codes, expected", [
        (["CS101"], 4.0), (["CS101", "CS201"], 1.71), ([], 0.0), (["EN101"], 0.0),
    ], ids=["single", "with-F-rounded", "empty", "ungraded-only"])
    def test_subsets(self, ali, codes, expected):
        assert ali.gpa(codes) == expected

    @pytest.mark.unit
    def test_accepts_generator(self, ali):
        assert ali.gpa(c.strip() for c in " CS101 ,MA101".split(",")) == 3.6

    @pytest.mark.negative
    @pytest.mark.parametrize("codes", [["CS101", "AI201"], ["cs101"]], ids=["not-enrolled", "wrong-case"])
    def test_unknown_code(self, ali, codes):
        with pytest.raises(KeyError):
            ali.gpa(codes)


class TestStudentSemesterGpa:
    @pytest.mark.smoke
    def test_semester_one(self, ali):
        assert ali.semester_gpa(1) == 3.6

    @pytest.mark.unit
    def test_fail_and_ungraded_semester(self, ali):
        assert ali.semester_gpa(2) == 0.0

    @pytest.mark.unit
    def test_only_ungraded_semester(self, seeded_school, ali):
        seeded_school.add_course("AI201", "AI", 3)
        seeded_school.enroll("CS-001", "AI201", 3)
        assert ali.semester_gpa(3) == 0.0

    @pytest.mark.negative
    @pytest.mark.parametrize("semester", [0, -1, 3])
    def test_semester_without_courses(self, ali, semester):
        with pytest.raises(KeyError):
            ali.semester_gpa(semester)


class TestStudentCgpa:
    @pytest.mark.smoke
    def test_seeded(self, ali):
        assert ali.cgpa() == 2.0  # 18 / 9

    @pytest.mark.unit
    def test_no_enrollments(self, empty_student):
        assert empty_student.cgpa() == 0.0

    @pytest.mark.unit
    def test_all_ungraded(self, empty_student):
        empty_student.enrollments["CS101"] = Enrollment(CS101, 1)
        assert empty_student.cgpa() == 0.0

    @pytest.mark.unit
    def test_changes_after_marks_entered(self, seeded_school, ali):
        seeded_school.enter_marks("CS-001", "EN101", 90)
        assert ali.cgpa() == 2.36  # 26 / 11
