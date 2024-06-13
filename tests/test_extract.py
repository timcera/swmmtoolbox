"""
test_extract
----------------------------------

Tests for `swmmtoolbox` module.
"""

import shlex

import pandas as pd
import pytest

from swmmtoolbox.swmmtoolbox import extract

try:
    from cStringIO import StringIO
except Exception:
    from io import StringIO

import subprocess

extract_node_fname = "tests/extract_node.csv"
extract_node = pd.read_csv(
    extract_node_fname,
    sep=",",
    skipinitialspace=True,
    parse_dates=True,
    index_col=0,
)

extract_link_fname = "tests/extract_link.csv"
extract_link = pd.read_csv(
    extract_link_fname,
    sep=",",
    skipinitialspace=True,
    parse_dates=True,
    index_col=0,
)


@pytest.mark.parametrize(
    "args, expected_output",
    [
        (
            "swmmtoolbox extract tests/frutal.out link,222,Flow_rate node,222,Hydraulic_head",
            extract_link.join(extract_node),
        ),
        ("swmmtoolbox extract tests/frutal.out link,222,Flow_rate", extract_link),
        ("swmmtoolbox extract tests/frutal.out node,222,Hydraulic_head", extract_node),
    ],
    ids=[
        "command_line_1",
        "command_line_1",
        "command_line_1",
    ],
)
def test_extract_command_line(args, expected_output):
    # Act
    args = shlex.split(args)
    complete = subprocess.run(args, capture_output=True, text=True, check=True)
    result = pd.read_csv(StringIO(complete.stdout), index_col=0, parse_dates=True)

    # Assert
    if expected_output is None:
        assert result is None
    else:
        pd.testing.assert_frame_equal(result, expected_output)


@pytest.mark.parametrize(
    "filename, labels, expected_output",
    [
        (
            "tests/frutal.out",
            [["link", "222", "Flow_rate"], ["node", 222, "Hydraulic_head"]],
            extract_link.join(extract_node),
        ),
        ("tests/frutal.out", [["link", "222", "Flow_rate"]], extract_link),
        ("tests/frutal.out", [["node", 222, "Hydraulic_head"]], extract_node),
    ],
    ids=[
        "python_api_1",
        "python_api_2",
        "python_api_3",
    ],
)
def test_extract_python_api(filename, labels, expected_output):
    # Act
    result = extract(filename, labels)

    result.index.name = "Datetime"

    # Assert
    if expected_output is None:
        assert result is None
    else:
        pd.testing.assert_frame_equal(result, expected_output)
