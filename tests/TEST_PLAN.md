# Test Plan: Student Management System

The application is in `../student-management-system`. Three of its modules are under test, lowest level first:

| # | Module | What it does | Test file |
|---|--------|--------------|-----------|
| 1 | `sms/grading.py` | Marks → letter grade, credit-weighted GPA | `test_grading.py` |
| 2 | `sms/models.py` | `Enrollment` (grade of one course), `Student` (enrollments, GPA, semester GPA, CGPA) | `test_models.py` |
| 3 | `sms/school.py` | `School`: adds students/courses, enrolls, enters marks, validates every change | `test_school.py` |

Techniques: **ECP** (equivalence class partitioning: one value per class), **BVA** (boundary value analysis: on, just below, and just above every boundary), **error guessing** (empty, `None`, wrong case, duplicates, ungraded courses).

---

## Module 1: `sms.grading`

### `calculate_grade(marks)`

Grading scale (lower bound inclusive):

| Marks | 85–100 | 80–<85 | 75–<80 | 70–<75 | 65–<70 | 60–<65 | 55–<60 | 50–<55 | 0–<50 |
|-------|--------|--------|--------|--------|--------|--------|--------|--------|-------|
| Grade | A 4.0 | A- 3.7 | B+ 3.3 | B 3.0 | B- 2.7 | C+ 2.3 | C 2.0 | D 1.0 | F 0.0 |

**ECP:** 9 valid classes, one per band. Nominal values: 92, 82, 77, 72, 67, 62, 57, 52, 25.
Out-of-contract classes: marks < 0 and marks > 100.

**BVA:** every band's lower bound and the value 0.01 below it:
85/84.99, 80/79.99, 75/74.99, 70/69.99, 65/64.99, 60/59.99, 55/54.99, 50/49.99, plus the ends of the range 0 and 100.

**Other:** an int and the equal float give the same grade (`70` vs `70.0`), and the result is a `(letter, points)` tuple.

### `calculate_gpa(enrollments)`

**ECP:**
- empty input → 0.0
- all courses ungraded (`marks=None`) → 0.0 (no divide-by-zero)
- one graded course → that course's grade points
- several courses with different credit hours → credit-weighted mean
- graded and ungraded mixed → ungraded ones ignored
- any iterable, including a generator (that is how `Student.gpa` calls it)

**BVA:** all F → 0.0 (minimum), all A → 4.0 (maximum). Results that are not exact are rounded to 2 decimals (12/7 → 1.71).

---

## Module 2: `sms.models`

### `Enrollment.grade` / `Enrollment.grade_points`

**ECP:** marks not entered (`None`) → `None` / `None`. Marks entered → letter and points from the scale.
**BVA:** 0 → F (0 is falsy but is a real mark, so it must not be treated as "not entered"), 49.99 → F, 50 → D, 85 → A, 100 → A.
**Other:** a new enrollment has no marks. Changing the marks changes the grade (nothing is cached).

### `Student.enrollment(code)`

**ECP:** enrolled code → the enrollment. Code not enrolled → `KeyError`.
**Error guessing:** wrong case (`cs101`), empty code, student with no enrollments, error message names the student and the code.

### `Student.semesters()`

**ECP:** no enrollments → `[]`; several courses in a semester → that semester listed once.
**Other:** output is sorted even when courses were added out of order, and gaps are kept (`[1, 3]`).

### `Student.gpa(codes)`

**ECP:** subset of courses, single course, empty list → 0.0, only ungraded courses → 0.0, generator input.
**Invalid:** any code the student is not enrolled in → `KeyError`, including wrong case.

### `Student.semester_gpa(semester)`

**ECP:** semester with graded courses, semester with an F and an ungraded course, semester with only ungraded courses → 0.0.
**BVA / invalid:** 0, -1, and the semester after the last one → `KeyError`.

### `Student.cgpa()`

**ECP:** all enrollments, no enrollments → 0.0, all ungraded → 0.0, value changes after marks are entered.

---

## Module 3: `sms.school.School`

### `add_student(roll_no, name, program)`

**ECP valid:** normal data. **Invalid:** empty or `None` roll no, empty or `None` name, duplicate roll no → `ValueError`.
**BVA:** 1-character roll no and name are valid; empty string (length 0) is invalid.
**Error guessing:** roll numbers are case-sensitive here (`cs-001` ≠ `CS-001`; the CLI uppercases them before calling). A duplicate does not overwrite the existing student.

### `add_course(code, title, credit_hours)`

**ECP valid:** normal data. **Invalid:** empty code, empty title, duplicate code, non-positive credit hours → `ValueError`.
**BVA on credit hours:** -1 and 0 invalid; 1 (lowest valid) and 6 valid.
**Other:** a rejected course is not stored; a duplicate does not overwrite.

### `enroll(roll_no, code, semester)`

**ECP valid:** known student, known course, semester ≥ 1. **Invalid:** unknown student / unknown course → `KeyError`; already enrolled, semester < 1 → `ValueError`.
**BVA on semester:** -1 and 0 invalid; 1 (lowest valid) and 8 valid.
**Other:** a new enrollment has no marks, and a rejected enrollment leaves the student unchanged.

### `enter_marks(roll_no, code, marks)`

**ECP valid:** 0–100. **Invalid:** < 0, > 100 → `ValueError`; unknown student, course not enrolled → `KeyError`.
**BVA:** -1, -0.01, **0**, 0.01, 50, 99.99, **100**, 100.01, 101.
**Other:** entering marks again overwrites them. Rejected marks leave the old marks in place.

### `student(roll_no)` / `course(code)`

**ECP:** existing key → the stored object (same instance). Missing key → `KeyError`. **Error guessing:** wrong case, empty key.

---

## Data-driven tests (CSV)

`test_data_driven.py` reads its cases from `data/*.csv`. The same cases are listed in `test_cases.xlsx`.

| File | Function under test | Cases |
|------|---------------------|-------|
| `enter_marks_cases.csv` | `School.enter_marks` + `Enrollment.grade` | `TC-DD-01`…`TC-DD-12` (valid boundaries, invalid range, unknown student/course) |
| `gpa_cases.csv` | `calculate_gpa` | `TC-GPA-01`…`TC-GPA-10` (empty, ungraded, weighting, rounding) |

---

## Observations found while planning

These are not failing tests. The tests check the behaviour as it is today, and these points are open questions for the developers:

1. `calculate_grade` does not check the range: `-1` returns `None`, `150` returns `"A"`. The range is only enforced in `School.enter_marks`.
2. `add_course` has no upper limit on credit hours, and `enroll` has no upper limit on semester.
3. `add_student` does not validate `program`; an empty program is accepted.
4. `enter_marks` checks the marks range before it looks up the student, so bad marks for an unknown student raise `ValueError`, not `KeyError`.
