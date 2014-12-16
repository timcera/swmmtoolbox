#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_listdetail
----------------------------------

Tests for `swmmtoolbox` module.
"""
import shlex
import subprocess
import os
from pandas.util.testing import TestCase
from pandas.util.testing import assert_frame_equal, assert_equal
import sys
try:
    from cStringIO import StringIO
except:
    from io import StringIO

import pandas as pd

from swmmtoolbox import swmmtoolbox


def capture(func, *args, **kwds):
    sys.stdout = StringIO()      # capture output
    out = func(*args, **kwds)
    out = sys.stdout.getvalue()  # release output
    try:
        out = bytes(out, 'utf-8')
    except:
        pass
    return out


class TestListdetail(TestCase):
    def setUp(self):
        listdetail_node_fname = os.path.join('tests', 'listdetail_node.csv')
        self.listdetail_node = open(listdetail_node_fname).readlines()

        listdetail_link_fname = os.path.join('tests', 'listdetail_link.csv')
        self.listdetail_link = open(listdetail_link_fname).readlines()


    def test_listdetail_node(self):
        out = capture(swmmtoolbox.listdetail, os.path.join('tests', 'frutal.out'), 'node')
        self.maxDiff = None
        assert_equal(out, ''.join(self.listdetail_node))

    def test_listdetail_link(self):
        out = capture(swmmtoolbox.listdetail, os.path.join('tests', 'frutal.out'), 'link')
        self.maxDiff = None
        assert_equal(out, ''.join(self.listdetail_link))

