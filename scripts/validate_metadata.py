from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - handled at runtime
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "codemeta.json",
    ".zenodo.json",
    "ro-crate-metadata.json",
    "scripts/generate_ro_crate.py",
    "scripts/validate_metadata.py",
]

EXPECTED_TITLE = "Interactive Distributed Provenance Example (DPC/DSC)"
EXPECTED_LICENSE = "Apache-2.0"
EXPECTED_ORCID = "0000-0001-8260-231X"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required to parse CITATION.cff.")
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def find_entity(graph: list[dict], entity_id: str) -> dict | None:
    for entity in graph:
        if entity.get("@id") == entity_id:
            return entity
    return None


def iter_ro_crate_files(root: Path) -> list[Path]:
    return sorted(root.rglob("ro-crate-metadata.json"))


def validate_haspart_paths(crate_path: Path, errors: list[str]) -> None:
    crate_dir = crate_path.parent
    crate = load_json(crate_path)
    graph = crate.get("@graph", [])
    root = find_entity(graph, "./")
    if not root:
        errors.append(f"{crate_path} missing root dataset (@id ./)")
        return
    has_part = root.get("hasPart", [])
    for part in has_part:
        part_id = part.get("@id") if isinstance(part, dict) else part
        if not isinstance(part_id, str):
            continue
        if part_id.startswith("http://") or part_id.startswith("https://") or part_id.startswith("#"):
            continue
        if part_id.startswith("/"):
            errors.append(f"{crate_path}: hasPart @id must be relative, got absolute path {part_id}")
            continue
        if part_id.startswith("./"):
            target = crate_dir / part_id[2:]
        else:
            target = crate_dir / part_id
        if not target.exists():
            errors.append(f"{crate_path}: hasPart @id does not resolve: {part_id}")


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        path = REPO_ROOT / rel
        ensure(path.exists(), f"Missing required file: {rel}", errors)

    if errors:
        print("Metadata validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    readme_text = read_text(REPO_ROOT / "README.md")
    ensure("Live demo" in readme_text, "README missing Live demo section", errors)
    ensure("..." not in readme_text, "README contains ellipsis '...'", errors)

    citation = load_yaml(REPO_ROOT / "CITATION.cff")
    codemeta = load_json(REPO_ROOT / "codemeta.json")
    zenodo = load_json(REPO_ROOT / ".zenodo.json")
    ro_crate = load_json(REPO_ROOT / "ro-crate-metadata.json")

    ensure(citation.get("title") == EXPECTED_TITLE, "CITATION title mismatch", errors)
    ensure(codemeta.get("name") == EXPECTED_TITLE, "CodeMeta name mismatch", errors)
    ensure(zenodo.get("title") == EXPECTED_TITLE, "Zenodo title mismatch", errors)

    ensure(citation.get("license") == EXPECTED_LICENSE, "CITATION license mismatch", errors)
    ensure(codemeta.get("license") == EXPECTED_LICENSE, "CodeMeta license mismatch", errors)
    ensure(zenodo.get("license") == EXPECTED_LICENSE, "Zenodo license mismatch", errors)

    author_orcid = (
        citation.get("authors", [{}])[0].get("orcid", "").replace("https://orcid.org/", "")
    )
    ensure(author_orcid == EXPECTED_ORCID, "CITATION ORCID mismatch", errors)
    ensure(
        codemeta.get("author", {}).get("@id", "").endswith(EXPECTED_ORCID),
        "CodeMeta ORCID mismatch",
        errors,
    )
    zenodo_orcid = zenodo.get("creators", [{}])[0].get("orcid", "")
    ensure(
        zenodo_orcid == EXPECTED_ORCID or zenodo_orcid.endswith(EXPECTED_ORCID),
        "Zenodo ORCID mismatch",
        errors,
    )

    versions = set()
    for value in (
        citation.get("version"),
        codemeta.get("version"),
        zenodo.get("version"),
    ):
        if value:
            versions.add(value)
    ensure(len(versions) <= 1, "Version mismatch across metadata files", errors)

    for path in [
        REPO_ROOT / "CITATION.cff",
        REPO_ROOT / "codemeta.json",
        REPO_ROOT / ".zenodo.json",
        REPO_ROOT / "ro-crate-metadata.json",
    ]:
        ensure("..." not in read_text(path), f"{path.name} contains ellipsis '...'", errors)

    graph = ro_crate.get("@graph", [])
    ensure(isinstance(graph, list), "RO-Crate @graph missing or invalid", errors)
    root = find_entity(graph, "./")
    descriptor = find_entity(graph, "ro-crate-metadata.json")

    ensure(root is not None, "RO-Crate root dataset missing", errors)
    if root:
        root_types = root.get("@type", [])
        if isinstance(root_types, str):
            root_types = [root_types]
        ensure("Dataset" in root_types, "RO-Crate root dataset is not a Dataset", errors)

    ensure(descriptor is not None, "RO-Crate metadata descriptor missing", errors)
    if descriptor:
        conforms = descriptor.get("conformsTo", [])
        if isinstance(conforms, dict):
            conforms = [conforms]
        conforms_ids = {item.get("@id") for item in conforms if isinstance(item, dict)}
        ensure(
            "https://w3id.org/ro/crate/1.1" in conforms_ids,
            "RO-Crate descriptor missing conformsTo RO-Crate 1.1",
            errors,
        )

    for crate_path in iter_ro_crate_files(REPO_ROOT):
        validate_haspart_paths(crate_path, errors)

    if errors:
        print("Metadata validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Metadata validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

