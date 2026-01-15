from __future__ import annotations

from pathlib import Path

from rocrate.model.contextentity import ContextEntity
from rocrate.rocrate import ROCrate

REPO_ROOT = Path(__file__).resolve().parents[1]
ORCID = "https://orcid.org/0000-0001-8260-231X"


def add_file(crate: ROCrate, path: Path, *, name: str | None = None) -> object | None:
    if not path.exists():
        return None
    rel_path = path.relative_to(REPO_ROOT).as_posix()
    properties = {}
    if name:
        properties["name"] = name
    return crate.add_file(source=str(path), dest_path=rel_path, properties=properties)


def add_dataset(crate: ROCrate, path: Path, *, name: str | None = None) -> object | None:
    if not path.exists():
        return None
    rel_path = path.relative_to(REPO_ROOT).as_posix()
    properties = {}
    if name:
        properties["name"] = name
    return crate.add_dataset(source=str(path), dest_path=rel_path, properties=properties)


def main() -> None:
    crate = ROCrate()

    creator = crate.add(
        ContextEntity(
            crate,
            ORCID,
            properties={"@type": "Person", "name": "Augustus Ellerm"},
        )
    )

    viewer = crate.add(
        ContextEntity(
            crate,
            "#viewer",
            properties={
                "@type": "SoftwareSourceCode",
                "name": "Interactive Distributed Provenance Example (DPC/DSC)",
                "description": "Viewer used to browse the DPC/DSC example crates.",
                "codeRepository": "https://github.com/GusEllerm/distributed-provenance-example",
                "license": "Apache-2.0",
                "version": "1.0.1",
            },
        )
    )

    root = crate.root_dataset
    root["name"] = "Interactive Distributed Provenance Example (DPC/DSC)"
    root["description"] = (
        "Interactive RO-Crate viewer and example Distributed Provenance Crate (DPC) and "
        "Distributed Step Crate (DSC) data used to browse and inspect distributed provenance records."
    )
    root["license"] = "Apache-2.0"
    root["version"] = "1.0.1"
    root["identifier"] = "https://doi.org/10.5281/zenodo.18253439"
    root["creator"] = creator
    root["mainEntity"] = viewer

    parts = [
        add_file(crate, REPO_ROOT / "README.md", name="Repository README"),
        add_file(crate, REPO_ROOT / "index.html", name="Viewer entrypoint"),
        add_file(crate, REPO_ROOT / "comparator.py", name="Comparison utility"),
        add_file(crate, REPO_ROOT / "validation_rules.json", name="Validation rules"),
        add_dataset(
            crate,
            REPO_ROOT / "Distributed_Provenance_Crate",
            name="Distributed Provenance Crate example",
        ),
        add_dataset(
            crate,
            REPO_ROOT / "e7beae76-bf36-4484-bcc7-9ad133b0c5e2",
            name="Distributed Step Crates (DSC) examples",
        ),
        add_dataset(
            crate,
            REPO_ROOT / "validation",
            name="Validation outputs and summaries",
        ),
        add_file(crate, REPO_ROOT / "CITATION.cff", name="Citation metadata"),
        add_file(crate, REPO_ROOT / "codemeta.json", name="CodeMeta metadata"),
        add_file(crate, REPO_ROOT / ".zenodo.json", name="Zenodo metadata"),
        add_file(crate, REPO_ROOT / "LICENSE", name="License"),
        add_file(crate, REPO_ROOT / "scripts/generate_ro_crate.py", name="RO-Crate generator"),
        add_file(crate, REPO_ROOT / "scripts/validate_metadata.py", name="Metadata validator"),
    ]

    root["hasPart"] = [part for part in parts if part is not None]

    crate.metadata.write(REPO_ROOT)


if __name__ == "__main__":
    main()

