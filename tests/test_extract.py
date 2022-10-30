"""
test_extract
----------------------------------

Tests for `swmmtoolbox` module.
"""
import os
import sys
from unittest import TestCase

from pandas.util.testing import assert_frame_equal

try:
    from cStringIO import StringIO
except:
    from io import StringIO

import pandas as pd

from swmmtoolbox import swmmtoolbox


def capture(func, *args, **kwds):
    sys.stdout = StringIO()  # capture outputA
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        return bytes(out, "utf-8")
    except:
        return out


class Testextract(TestCase):
    def setUp(self):
        extract_node_fname = os.path.join("tests", "extract_node.csv")
        self.extract_node = pd.read_csv(
            extract_node_fname,
            sep=",",
            skipinitialspace=True,
            parse_dates=True,
            index_col=0,
        )

        extract_link_fname = os.path.join("tests", "extract_link.csv")
        self.extract_link = pd.read_csv(
            extract_link_fname,
            sep=",",
            skipinitialspace=True,
            parse_dates=True,
            index_col=0,
        )

    def test_extract_node(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"), "node,222,Hydraulic_head"
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        assert_frame_equal(out, self.extract_node)

    def test_extract_link(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"), "link,222,Flow_rate"
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        assert_frame_equal(out, self.extract_link)

    def test_labels_str(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            "link,222,Flow_rate node,222,Hydraulic_head",
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)

    def test_labels_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            ["link,222,Flow_rate node,222,Hydraulic_head"],
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)

    def test_labels_list_strs(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            ["link,222,Flow_rate", "node,222,Hydraulic_head"],
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)

    def test_extract_node_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"), ["node", 222, "Hydraulic_head"]
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        assert_frame_equal(out, self.extract_node)

    def test_extract_link_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"), ["link", 222, "Flow_rate"]
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        assert_frame_equal(out, self.extract_link)

    def test_labels_str_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            [["link", 222, "Flow_rate"], ["node", 222, "Hydraulic_head"]],
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)

    def test_labels_list_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            [["link", 222, "Flow_rate"], ["node", 222, "Hydraulic_head"]],
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)

    def test_labels_list_strs_list(self):
        out = swmmtoolbox.extract(
            os.path.join("tests", "frutal.out"),
            [["link", 222, "Flow_rate"], "node,222,Hydraulic_head"],
        )
        out.index.name = "Datetime"
        self.maxDiff = None
        ndf = self.extract_link.join(self.extract_node)
        assert_frame_equal(out, ndf)
