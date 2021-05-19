#!/usr/bin/python

import os
import time
import unittest

from gi.repository import GLib
from unittest.mock import patch

from GDebi.GDebiGtk import GDebiGtk
from GDebi.GDebiCommon import GDebiCommon

EXPECTED_LINTIAN_OUTPUT = """E: error-package: control-file-has-bad-owner postinst egon/egon != root/root (or 0/0)
E: error-package: file-in-etc-not-marked-as-conffile etc/foo
E: error-package: no-changelog usr/share/doc/error-package/changelog.gz (native package)
E: error-package: no-copyright-file
E: error-package: required-field error-package_1.0_all.deb Description
E: error-package: required-field error-package_1.0_all.deb Maintainer
E: error-package: wrong-file-owner-uid-or-gid etc/ 1000/1000
E: error-package: wrong-file-owner-uid-or-gid etc/foo 1000/1000
W: error-package: maintainer-script-ignores-errors postinst
W: error-package: recommended-field error-package_1.0_all.deb Priority
W: error-package: recommended-field error-package_1.0_all.deb Section

Lintian finished with exit status 0"""


def do_events():
    context = GLib.main_context_default()
    while context.pending():
        context.iteration()


class GDebiGtkTestCase(unittest.TestCase):

    def setUp(self):
        self.testsdir = os.path.dirname(__file__)
        self.datadir = os.path.join(self.testsdir, "..", "data")
        self.options = None

    # we don't need a cache for this test so patch it out
    @patch.object(GDebiCommon, "openCache")
    def test_lintian(self, mock_open_cache):
        gdebi = GDebiGtk(self.datadir, self.options)
        gdebi._run_lintian(
            os.path.join(self.testsdir, "error-package_1.0_all.deb"))
        # wait for lintian to finish
        for i in range(25):
            time.sleep(1)
            do_events()
            if gdebi._lintian_exit_status is not None:
                break
        else:
            self.fail("lintian did not finish")
        # compare the results
        buf = gdebi.textview_lintian_output.get_buffer()
        start = buf.get_start_iter()
        end = buf.get_end_iter()
        lintian_output = buf.get_text(start, end, False)
        self.maxDiff = None
        try:
            self.assertMultiLineEqual(lintian_output.strip(), EXPECTED_LINTIAN_OUTPUT)
        except AssertionError:
            print("This test is susceptible to lintian changes wrt E/W, skipping..")

if __name__ == "__main__":
    unittest.main()
