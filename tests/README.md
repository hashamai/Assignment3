# Running the tests

The tests live outside the application. They test `../student-management-system`; `pytest.ini` puts that folder on the import path.

```
Assignment3/
  student-management-system/   the application under test (unchanged)
  tests/                       this folder
    pytest.ini                 puts the application on the import path
    requirements-test.txt      pytest, pytest-xdist
    TEST_PLAN.md               ECP/BVA notes for each module (what is tested and why)
    conftest.py                shared fixtures
    test_grading.py            module 1: sms.grading
    test_models.py             module 2: sms.models (Enrollment, Student)
    test_school.py             module 3: sms.school (School)
    test_data_driven.py        cases read from data/*.csv
    data/                      enter_marks_cases.csv, gpa_cases.csv
    test_cases.xlsx            the data-driven cases as an Excel test case sheet
```

## Setup (once)

From inside this `tests` folder:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
```

Run every command below from inside this `tests` folder. After `source .venv/bin/activate` you can type `pytest` in place of `.venv/bin/pytest`.

## Run

| What | Command |
|------|---------|
| All tests | `.venv/bin/pytest -v` |
| All tests in parallel (one worker per CPU) | `.venv/bin/pytest -n auto` |
| One module's file | `.venv/bin/pytest test_school.py` |
| One function's tests (by name) | `.venv/bin/pytest -k enter_marks` |
| One CSV case | `.venv/bin/pytest -k TC-DD-08` |

Tests run file by file in alphabetical order, and top to bottom inside each file.

## Parameterization and data-driven tests

- Unit tests use `@pytest.mark.parametrize` for ECP classes and BVA boundaries. Each row shows up as its own test, e.g. `test_bva_band_edges[84.99-A-]`.
- `test_data_driven.py` reads one test per CSV row. To add a case, add a row to `data/enter_marks_cases.csv` or `data/gpa_cases.csv`; no code change is needed. The `tc_id` column becomes the test's name, so a failure points straight at the row in `test_cases.xlsx`.
