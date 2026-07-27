from __future__ import annotations

from phase18_cutover_contract import *


def source_ref_manifest_paths() -> set[Path]:
    return {Path(path) for path in SOURCE_REF_ROW_COLLECTIONS}


def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(
            f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(
            f"{row_name} source ref must include file and row ID: {source_ref}"
        )
    relative_path = require_repo_relative(path_text, row_name)
    if relative_path not in source_ref_manifest_paths():
        raise VerificationError(
            f"{row_name} source ref path is not an approved Phase 18 source manifest: {source_ref}"
        )
    data = load_json(root, relative_path)
    collection_name, key_name = SOURCE_REF_ROW_COLLECTIONS[
        relative_path.as_posix()]
    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(
            f"{row_name} source ref collection is missing: {source_ref}")
    matches = [
        f"{collection_name}[{index}]" for index, candidate in enumerate(rows)
        if isinstance(candidate, dict) and candidate.get(key_name) == row_id
    ]
    if not matches:
        raise VerificationError(
            f"{row_name} source ref row not found in approved row collections: {source_ref}"
        )
    if len(matches) > 1:
        raise VerificationError(
            f"{row_name} source ref row matches multiple approved rows: {source_ref}"
        )


def retained_surface_source_refs(root: Path) -> set[str]:
    refs: set[str] = set()
    for path in RETAINED_SURFACE_SOURCE_PATHS:
        data = load_json(root, path)
        collection_name, key_name = SOURCE_REF_ROW_COLLECTIONS[path]
        rows = data.get(collection_name)
        if not isinstance(rows, list):
            raise VerificationError(
                f"{path} must contain {collection_name} list")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise VerificationError(
                    f"{path} {collection_name}[{index}] must be an object")
            row_id = row.get(key_name)
            if not isinstance(row_id, str) or not row_id:
                raise VerificationError(
                    f"{path} {collection_name}[{index}] {key_name} must be a non-empty string"
                )
            refs.add(f"{path}#{row_id}")
    return refs
