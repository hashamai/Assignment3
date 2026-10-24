# Running the tests

The tests live outside the application. They test `../student-management-system`; `pytest.ini` puts that folder on the import path.

```
Assignment3/
  student-management-system/   the application under test (unchanged)
  tests/                       this folder
    pytest.ini                 markers, import path, parallel settings
    requirements-test.txt      pytest, pytest-xdist
    TEST_PLAN.md               ECP/BVA notes for each module (what is tested and why)
    conftest.py                shared fixtures and the execution order of groups
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
| All tests, in the configured order | `.venv/bin/pytest -v` |
| All tests in parallel (one worker per CPU) | `.venv/bin/pytest -n auto` |
| Parallel with 4 workers | `.venv/bin/pytest -n 4` |
| One module's file | `.venv/bin/pytest test_school.py` |
| One function's tests | `.venv/bin/pytest "test_school.py::TestEnterMarks"` |
| One CSV case | `.venv/bin/pytest -k TC-DD-08` |

## Groups and suites

Each test has a **group** marker and a **module** marker (see `pytest.ini`). Select a suite with `-m`:

| Suite | Command |
|-------|---------|
| Smoke (quick happy-path checks) | `.venv/bin/pytest -m smoke` |
| Unit (ECP/BVA) | `.venv/bin/pytest -m unit` |
| Negative (invalid input, errors) | `.venv/bin/pytest -m negative` |
| Data-driven (CSV) | `.venv/bin/pytest -m data_driven` |
| One module | `.venv/bin/pytest -m grading` (or `models`, `school`) |
| Combined | `.venv/bin/pytest -m "school and negative"`, `.venv/bin/pytest -m "not data_driven"` |

## Execution order

`conftest.py` sorts the collected tests:

1. by group: `smoke` → `unit` → `negative` → `data_driven`
2. then by module, lowest level first: `grading` → `models` → `school`
3. then in the order they are written in the file.

To change the order, edit `GROUP_ORDER` / `MODULE_ORDER` in `conftest.py`. Check the order without running anything: `.venv/bin/pytest --collect-only -q`.

A parallel run (`-n`) splits work across processes, so tests from different files run at the same time. `--dist loadfile` in `pytest.ini` keeps each file on one worker, so tests inside a file still run in order. Run without `-n` when you need the full group order.

## Parameterization and data-driven tests

- Unit tests use `@pytest.mark.parametrize` for ECP classes and BVA boundaries. Each row shows up as its own test, e.g. `test_bva_band_edges[84.99-A-]`.
- `test_data_driven.py` reads one test per CSV row. To add a case, add a row to `data/enter_marks_cases.csv` or `data/gpa_cases.csv`; no code change is needed. The `tc_id` column becomes the test's name, so a failure points straight at the row in `test_cases.xlsx`.
