# Example: Distributed Provenance-Aware Workflow using Distributed Step Crate Extension

This repository provides an example of a **Distributed Provenance-Aware Workflow**, using the **Distributed Step Crate extension** applied to the **Provenance Run Crate** specification. It is implemented in the context of a real production Workflow Management System (WMS): **Globus Flows**.

---

## 📦 Contents

```
/
├── index.html                          # Entry point for web-based preview
├── ProvenanceRunCrate/                # Main Provenance Run Crate
│   └── ro-crate-preview.html
└── e7beae76-bf36-4484-bcc7-9ad133b0c5e2/
    ├── 395cdbd9-5b81-49a2-a7ae-9d84a8f70428/
    │   └── ro-crate-preview.html      # Distributed Step Crate 1
    └── 88102f1e-8d80-43c8-ab8b-6006458475f3/
        └── ro-crate-preview.html      # Distributed Step Crate 2
```

Each **Distributed Step Crate** corresponds to a granular step in the overall workflow, executed independently via Globus Flows and collated within an Orchestration Node. The full **Provenance Run Crate** extension integrates these **Distributed Step Crates** to provide a contiguous provenance record of the distributed workflow's run.

---

## 🌐 Web Preview

This repository includes a minimal GitHub Pages site to preview the RO-Crate visualizations via `ro-crate-preview.html`.

---

## 🧾 License

This work is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** License.
You are free to share and adapt the materials for any purpose, provided appropriate credit is given.

More information: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)

---

## 🔗 References

- [RO-Crate Specification](https://www.researchobject.org/ro-crate/)
- [Provenance Run Crate](https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/)
- [Globus Flows](https://www.google.com/search?client=safari&rls=en&q=Globus+FLows&ie=UTF-8&oe=UTF-8)
