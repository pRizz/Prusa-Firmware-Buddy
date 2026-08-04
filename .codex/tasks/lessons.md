## lesson-label-negative-architecture-checks | 2026-08-03 16:35

1. Date: 2026-08-03 16:35 CDT
2. What went wrong: The Darwin Bazel command was presented as a recovery/verification command without clearly leading with the fact that it was an intentional negative host-rejection test, making it appear that the workflow was trying to perform the positive embedded build on the wrong architecture.
3. Preventive rule: Whenever qualification has separate positive and negative host paths, label every command before execution as either `positive qualification` or `expected-failure host rejection`, and state the expected exit code and execution architecture.
4. Trigger signal to catch it earlier: A command runs on a host that the phase contract explicitly marks unsupported while a different container/CI architecture owns positive qualification.
