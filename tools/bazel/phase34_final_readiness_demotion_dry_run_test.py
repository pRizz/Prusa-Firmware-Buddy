#!/usr/bin/env python3
from __future__ import annotations

from phase34_final_readiness_cases_test import (
    Phase34FinalReadinessCasesMixin,
)
from phase34_final_readiness_demotion_failure_test import (
    Phase34FinalReadinessDemotionFailureMixin,
)
from phase34_final_readiness_source_failure_test import (
    Phase34FinalReadinessSourceFailureMixin,
)
from phase34_test_support import *


class Phase34FinalReadinessDemotionDryRunTest(
        Phase34FinalReadinessCasesMixin,
        Phase34FinalReadinessDemotionFailureMixin,
        Phase34FinalReadinessSourceFailureMixin,
        Phase34TestSupport):
    pass


from phase34_publication_state_test import (
    Phase34PublicationStateSecurityTests,
)

if __name__ == "__main__":
    unittest.main()
