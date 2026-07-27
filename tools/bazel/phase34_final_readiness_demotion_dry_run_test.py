#!/usr/bin/env python3
from __future__ import annotations

import importlib
import textwrap

from phase34_test_support import *


class Phase34FinalReadinessDemotionDryRunTest(Phase34TestSupport):
    for _module_name in (
            "phase34_final_readiness_cases_test",
            "phase34_final_readiness_demotion_failure_test",
            "phase34_final_readiness_source_failure_test",
    ):
        _module = importlib.import_module(_module_name)
        exec(textwrap.dedent(_module.TEST_METHODS), globals(), locals())


_publication_tests = importlib.import_module("phase34_publication_state_test")
exec(_publication_tests.TEST_CLASSES, globals())

if __name__ == "__main__":
    unittest.main()
