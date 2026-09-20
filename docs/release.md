# MVP 0.1.0 release record

This document records the release decisions and validation boundary for the
first homoloQode MVP.

## Release metadata

| Item | Decision |
|---|---|
| Version | `0.1.0` |
| Supported Python | Python 3.12 |
| Intended Git tag | `v0.1.0` |
| Tag timing | After the MVP-10 pull request is merged and remote CI is green |
| Distribution | Repository source release; PyPI publication is deferred |
| Citation | No DOI or `CITATION.cff` for 0.1.0; cite authors, repository URL, version, and tag |
| API stability | Experimental; compatibility is not guaranteed before a stable release |

## Reproducibility contract

Runtime dependencies and the `dev` extra are declared in `pyproject.toml`.
The release candidate is validated with:

```bash
python -m pip install -e ".[dev]"
python -m coverage run -m pytest
python -m coverage report
```

CI repeats those checks on Windows and Ubuntu using Python 3.12, registers the
`homoloqode` kernel, and executes every committed notebook with a 180-second
cell timeout. Coverage must remain at 100% for both statements and branches.

## Release boundary

The release provides a reproducible small-code reference path from periodic
cellulation through CSS construction, error sampling, syndrome extraction,
decoding, residual classification, and experiment/visualization outputs. The
limitations listed in the README and changelog are deliberate non-goals for
0.1.0.

## External release gates

- Review by both collaborators.
- Green Windows and Ubuntu jobs on the MVP-10 pull request.
- Merge to `main`.
- Create Git tag `v0.1.0` after the preceding checks pass.
