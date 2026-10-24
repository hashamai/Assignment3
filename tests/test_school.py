"""Module 3: sms.school.School (cases from TEST_PLAN.md)."""
import pytest

pytestmark = pytest.mark.school


class TestAddStudent:
    @pytest.mark.smoke
    def test_adds_student(self, school):
        school.add_student("CS-001", "Ali Khan", "BSCS")
        s = school.student("CS-001")
        assert (s.roll_no, s.name, s.program, s.enrollments) == ("CS-001", "Ali Khan", "BSCS", {})

    @pytest.mark.unit
    def test_bva_one_character_fields(self, school):
        school.add_student("1", "A", "B")
        assert "1" in school.students

    @pytest.mark.unit
    def test_empty_program_accepted(self, school):
        school.add_student("CS-001", "Ali Khan", "")  # TEST_PLAN observation 3
        assert school.student("CS-001").program == ""

    @pytest.mark.unit
    def test_roll_no_is_case_sensitive(self, school):
        school.add_student("CS-001", "Ali Khan", "BSCS")
        school.add_student("cs-001", "Other", "BSCS")
        assert len(school.students) == 2

    @pytest.mark.negative
    @pytest.mark.parametrize("roll_no, name", [("", "Ali"), ("CS-001", ""), (None, "Ali"), ("CS-001", None)],
                             ids=["empty-roll", "empty-name", "none-roll", "none-name"])
    def test_missing_required_field(self, school, roll_no, name):
        with pytest.raises(ValueError, match="required"):
            school.add_student(roll_no, name, "BSCS")
        assert school.students == {}

    @pytest.mark.negative
    def test_duplicate_does_not_overwrite(self, seeded_school):
        with pytest.raises(ValueError, match="already exists"):
            seeded_school.add_student("CS-001", "Someone Else", "BSSE")
        assert seeded_school.student("CS-001").name == "Ali Khan"


class TestAddCourse:
    @pytest.mark.smoke
    def test_adds_course(self, school):
        school.add_course("CS101", "Programming", 3)
        c = school.course("CS101")
        assert (c.code, c.title, c.credit_hours) == ("CS101", "Programming", 3)

    @pytest.mark.unit
    @pytest.mark.parametrize("credit_hours", [1, 6], ids=["lowest-valid", "high"])
    def test_bva_valid_credit_hours(self, school, credit_hours):
        school.add_course("CS101", "Programming", credit_hours)
        assert school.course("CS101").credit_hours == credit_hours

    @pytest.mark.negative
    @pytest.mark.parametrize("credit_hours", [0, -1], ids=["zero", "negative"])
    def test_bva_invalid_credit_hours(self, school, credit_hours):
        with pytest.raises(ValueError, match="positive"):
            school.add_course("CS101", "Programming", credit_hours)
        assert school.courses == {}

    @pytest.mark.negative
    @pytest.mark.parametrize("code, title", [("", "Programming"), ("CS101", "")], ids=["empty-code", "empty-title"])
    def test_missing_required_field(self, school, code, title):
        with pytest.raises(ValueError, match="required"):
            school.add_course(code, title, 3)

    @pytest.mark.negative
    def test_duplicate_does_not_overwrite(self, seeded_school):
        with pytest.raises(ValueError, match="already exists"):
            seeded_school.add_course("CS101", "Other", 1)
        assert seeded_school.course("CS101").title == "Programming"


class TestEnroll:
    @pytest.fixture
    def school_with_ai(self, seeded_school):
        seeded_school.add_course("AI201", "Artificial Intelligence", 3)
        return seeded_school

    @pytest.mark.smoke
    def test_enrolls_without_marks(self, school_with_ai):
        school_with_ai.enroll("CS-001", "AI201", 3)
        e = school_with_ai.student("CS-001").enrollment("AI201")
        assert (e.course.code, e.semester, e.marks) == ("AI201", 3, None)

    @pytest.mark.unit
    @pytest.mark.parametrize("semester", [1, 8], ids=["lowest-valid", "high"])
    def test_bva_valid_semester(self, school_with_ai, semester):
        school_with_ai.enroll("CS-001", "AI201", semester)
        assert school_with_ai.student("CS-001").enrollment("AI201").semester == semester

    @pytest.mark.negative
    @pytest.mark.parametrize("semester", [0, -1], ids=["zero", "negative"])
    def test_bva_invalid_semester_leaves_student_unchanged(self, school_with_ai, semester):
        with pytest.raises(ValueError, match="Semester"):
            school_with_ai.enroll("CS-001", "AI201", semester)
        assert "AI201" not in school_with_ai.student("CS-001").enrollments

    @pytest.mark.negative
    @pytest.mark.parametrize("roll_no, code", [("CS-999", "AI201"), ("CS-001", "XX999")],
                             ids=["unknown-student", "unknown-course"])
    def test_unknown_student_or_course(self, school_with_ai, roll_no, code):
        with pytest.raises(KeyError):
            school_with_ai.enroll(roll_no, code, 1)

    @pytest.mark.negative
    def test_already_enrolled(self, seeded_school):
        with pytest.raises(ValueError, match="already enrolled"):
            seeded_school.enroll("CS-001", "CS101", 2)
        assert seeded_school.student("CS-001").enrollment("CS101").semester == 1


class TestEnterMarks:
    @pytest.mark.smoke
    def test_enters_marks(self, seeded_school):
        seeded_school.enter_marks("CS-001", "EN101", 81)
        assert seeded_school.student("CS-001").enrollment("EN101").marks == 81

    @pytest.mark.unit
    @pytest.mark.parametrize("marks", [0, 0.01, 50, 99.99, 100])
    def test_bva_valid_marks(self, seeded_school, marks):
        seeded_school.enter_marks("CS-001", "EN101", marks)
        assert seeded_school.student("CS-001").enrollment("EN101").marks == marks

    @pytest.mark.unit
    def test_re_entry_overwrites(self, seeded_school):
        seeded_school.enter_marks("CS-001", "CS101", 55)
        assert seeded_school.student("CS-001").enrollment("CS101").grade == "C"

    @pytest.mark.negative
    @pytest.mark.parametrize("marks", [-1, -0.01, 100.01, 101])
    def test_bva_invalid_marks_keep_old_marks(self, seeded_school, marks):
        with pytest.raises(ValueError, match="between 0 and 100"):
            seeded_school.enter_marks("CS-001", "CS101", marks)
        assert seeded_school.student("CS-001").enrollment("CS101").marks == 90

    @pytest.mark.negative
    @pytest.mark.parametrize("roll_no, code", [("CS-999", "CS101"), ("CS-001", "AI201")],
                             ids=["unknown-student", "not-enrolled"])
    def test_unknown_student_or_enrollment(self, seeded_school, roll_no, code):
        with pytest.raises(KeyError):
            seeded_school.enter_marks(roll_no, code, 70)

    @pytest.mark.negative
    def test_range_checked_before_lookup(self, seeded_school):
        with pytest.raises(ValueError):  # TEST_PLAN observation 4
            seeded_school.enter_marks("CS-999", "CS101", 101)


class TestLookups:
    @pytest.mark.smoke
    def test_returns_stored_objects(self, seeded_school):
        assert seeded_school.student("CS-001") is seeded_school.students["CS-001"]
        assert seeded_school.course("CS101") is seeded_school.courses["CS101"]

    @pytest.mark.negative
    @pytest.mark.parametrize("roll_no", ["CS-999", "cs-001", ""], ids=["missing", "wrong-case", "empty"])
    def test_missing_student(self, seeded_school, roll_no):
        with pytest.raises(KeyError, match="No student"):
            seeded_school.student(roll_no)

    @pytest.mark.negative
    @pytest.mark.parametrize("code", ["XX999", "cs101", ""], ids=["missing", "wrong-case", "empty"])
    def test_missing_course(self, seeded_school, code):
        with pytest.raises(KeyError, match="No course"):
            seeded_school.course(code)
