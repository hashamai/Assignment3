# Running the tests

These tests check the app in the `student-management-system` folder, which sits next to this `tests` folder. The app's own code is not changed.

## What is in this folder

- `pytest.ini`: pytest settings (where the app is, file order, groups)
- `requirements-test.txt`: the packages the tests need
- `TEST_PLAN.md`: what is tested in each module and why (ECP and BVA notes)
- `conftest.py`: sample data that every test can use
- `test_grading.py`: tests for `sms/grading.py`
- `test_models.py`: tests for `sms/models.py`
- `test_school.py`: tests for `sms/school.py`
- `test_data_driven.py`: tests that read their data from CSV files
- `data/`: the CSV files
- `test_cases.xlsx`: the CSV test cases written as an Excel sheet


## Setup (do this once)

Open a terminal inside this `tests` folder and run:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
```

This creates a `.venv` folder and installs pytest and two plugins into it:

- pytest-xdist, for running tests in parallel
- pytest-order, for setting the order of tests

Run all the commands below from inside this `tests` folder.


## Run the tests

Run all tests:

```bash
.venv/bin/pytest -v
```

Run all tests in parallel (uses every CPU core):

```bash
.venv/bin/pytest -n auto
```

Run only the tests whose name contains a word, for example `enter_marks`:

```bash
.venv/bin/pytest -k enter_marks
```

Run one test case from the CSV file, for example `TC-EM-08`:

```bash
.venv/bin/pytest -k TC-EM-08
```


## Groups and suites

Some tests have a label written above them:

- `@pytest.mark.smoke` marks a smoke test, one basic check for each function.
- `@pytest.mark.negative` marks a negative test, which gives the code bad input and expects it to be rejected.

Run only the smoke tests:

```bash
.venv/bin/pytest -m smoke
```

Run only the negative tests:

```bash
.venv/bin/pytest -m negative
```

Run everything except the negative tests:

```bash
.venv/bin/pytest -m "not negative"
```

Each file is also a group. Run one file like this:

```bash
.venv/bin/pytest test_school.py
```


## Execution order

In a normal run, tests run in this order:

1. The smoke tests run first. Each one has `@pytest.mark.order(1)`, `@pytest.mark.order(2)` and so on, and they run in that number order.
2. Then the remaining tests run file by file, in the order listed under `testpaths` in `pytest.ini`: grading, then models, then school, then data-driven.
3. Inside each file, tests run from top to bottom.

To change the order, change the numbers in `@pytest.mark.order(...)`, or change the order of the files under `testpaths`.

To see the order without running the tests:

```bash
.venv/bin/pytest --collect-only -q
```

Note: in a parallel run (`-n auto`), several files run at the same time, so this order is not kept. Tests inside one file still run top to bottom.


## Data-driven tests

`@pytest.mark.parametrize` runs the same test many times with different inputs. Each input shows up as its own test in the results.

`test_data_driven.py` reads its inputs from the CSV files in `data/`, and each row is one test case. To add a new test case, add a new row to the CSV file; you don't need to change any code.

The `tc_id` column (for example `TC-EM-01`) becomes the test's name, so you can match a result to its row in `test_cases.xlsx`.
