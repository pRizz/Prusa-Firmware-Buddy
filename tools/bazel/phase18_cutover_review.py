#!/usr/bin/env python3
from __future__ import annotations

from phase18_cutover_artifacts import *
from phase18_cutover_contract import *
from phase18_cutover_policy import *
from phase18_cutover_security import *
from phase18_cutover_source_refs import *
from phase18_cutover_upstream_policy import *
from phase18_cutover_validation import *


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    for path, required_values in WIRING_REQUIRED_TEXT.items():
        try:
            text = read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))
            continue
        for required_text in required_values:
            if required_text not in text:
                errors.append(
                    f"{path.as_posix()} missing required wiring text: {required_text}"
                )
    try:
        just_text = read_text(root, "justfile")
        recipe_index = just_text.find("phase18-verify:")
        tests_index = just_text.find(
            "\n    bazel run //tools/bazel:phase18_verify_tests\n",
            recipe_index)
        verify_index = just_text.find(
            "\n    bazel run //tools/bazel:phase18_verify\n", recipe_index)
        if recipe_index == -1 or tests_index == -1 or verify_index == -1:
            errors.append("justfile missing complete phase18-verify recipe")
        elif tests_index > verify_index:
            errors.append(
                "justfile phase18-verify must run phase18_verify_tests before phase18_verify"
            )
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Validate the Phase 18 retained-code cutover review contract.")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate only the Phase 18 source contract")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="write deterministic redacted Phase 18 review artifacts")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 18 inputs and generated artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel, workflow, and just wiring")
    parser.add_argument(
        "--decision-input",
        help="optional Phase 18 maintainer decision input JSON")
    parser.add_argument(
        "--upstream-results",
        help="optional Phase 18 upstream result consumption JSON")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 18 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        contract = check_contract(ROOT)
        if args.security_only:
            output_dir = contained_output_dir(ROOT, args.output_dir)
            run_security_scan(ROOT,
                              args.decision_input,
                              args.upstream_results,
                              output_dir,
                              contract=contract)
            print("Phase 18 security scan passed")
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 18 wiring passed")
            return 0
        if args.quick:
            decision_input = load_decision_input(ROOT, args.decision_input)
            upstream_results = load_upstream_results(ROOT,
                                                     args.upstream_results)
            run_manifest = write_quick_artifacts(ROOT, contract,
                                                 decision_input,
                                                 upstream_results,
                                                 args.output_dir)
            print(
                f"Phase 18 quick artifacts written; demotion_allowed={str(run_manifest['demotion_allowed']).lower()}"
            )
            return 0
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 18 cutover review contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
