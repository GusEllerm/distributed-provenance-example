# Interactive Distributed Provenance Example (DPC/DSC) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18253488.svg)](https://doi.org/10.5281/zenodo.18253488)

This repository contains the interactive **Distributed Provenance Crate (DPC)** and **Distributed Step Crate (DSC)** example used to browse and inspect a distributed provenance record in a web viewer. It provides a live, click-through demonstration of the DPC/DSC representations and includes the example crate data alongside validation outputs. It supports thesis Chapter 5 by serving as the interactive reference for the distributed provenance example.

**Live demo:** https://gusellerm.github.io/distributed-provenance-example/

## What’s included

- `Distributed_Provenance_Crate/` example DPC (Provenance Run Crate extension).
- `e7beae76-bf36-4484-bcc7-9ad133b0c5e2/` example DSCs (two step crates).
- `validation/` comparison outputs and rendered validation summary.
- `comparator.py` and `validation_rules.json` for shape/structure checks.

## How to run locally

```
python3 -m http.server 8000
```

Open `http://localhost:8000/index.html`.

## Schemas / terms

- LivePublication Interface Schemas (DPC/DSC) DOI: https://doi.org/10.5281/zenodo.18250033
- DPC terms: https://w3id.org/livepublication/interface-schemas/dpc
- DSC terms: https://w3id.org/livepublication/interface-schemas/dsc
- DPC/DSC context: https://w3id.org/livepublication/interface-schemas/contexts/lp-dscdpc/v1.jsonld

## How to cite

Use the Zenodo DOI once a release is published (see `CITATION.cff`).  
TODO: backfill the Zenodo DOI and release version after minting.

## License

Apache License 2.0. See `LICENSE`.
