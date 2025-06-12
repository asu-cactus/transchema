import subprocess
import pytest
import shlex

# Please add your test case to the list
test_cases = [
    ("--len_id 1 --target_id 1 --max_target_id 2 --model gpt-4o-mini", "1"),
    (
        "--len_id 2 --target_id 1 --max_target_id 2 --model gpt-4o-mini --intermediate_materialization",
        "1",
    ),
]


# Execute all test cases
@pytest.mark.parametrize("command, expected", test_cases)
def test_main(capsys, command, expected):
    full_command = ["python", "critique_data.py"] + shlex.split(command)
    result = subprocess.run(full_command, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    last_line = lines[-1].rstrip()
    assert last_line == expected
