# Sewlore Fabric Care

A dependency-free Python API and local command-line tool for checking paired fabric-care readings before comparing them. It produces accepted records and correction notes as separate CSV files. The template contains only the header; examples and test fixtures are explicitly hypothetical software inputs, not measurements of fabric.

Read the [Fabric Measurement Guide: Stretch, Recovery and Care](https://sewlore.com/pages/fabric-measurement-methods-guide) for the recording method and limits of the calculations. An [interactive CSV validator](https://sewlore-fabric-care-validator.streamlit.app/) is available separately; this package does not require Streamlit or upload data to that service.

## Install and run locally

Use Python 3.10 or later. Python 3.12 is the checked local environment. Install this project from its checkout or a built wheel:

```sh
python -m pip install .
sewlore-fabric-care --version
sewlore-fabric-care template --output blank.csv
sewlore-fabric-care validate readings.csv --accepted accepted.csv --corrections corrections.csv
```

The equivalent module invocation is `python -m sewlore_fabric_care`. Use `-` as the input for stdin or as **one** output destination for stdout. Both result destinations are required; their headers are written even when there are no records. Stdout contains only the selected CSV; stderr contains counts or a command error, not source readings.

```sh
sewlore-fabric-care template
sewlore-fabric-care validate - --accepted - --corrections corrections.csv
```

Existing output files are refused unless `--overwrite` is explicit. The two destinations must differ and cannot replace the input, even with `--overwrite`. Parent directories must already exist. An I/O failure during writing may leave partial output; inspect both files after a command error.

| Exit code | Meaning |
|---|---|
| `0` | No correction entries, including a valid header-only input. |
| `1` | Correction entries exist; separate exports were written. |
| `2` | Usage, path or I/O error; exports may be absent or partial. |

## Strict default policy

The CLI and `validate_submission(bytes)` use the same restrictions as the original hosted validator: UTF-8 with optional BOM, at most **128 KiB**, and at most **250 non-empty records**. The exact ten-column header is:

```csv
sample_id,before_unit,after_unit,before_length,before_width,after_length,after_width,care_method,rectangle_assumption,notes
```

Use `sample-` followed by 1–6 digits, such as `sample-001`. Before and after units must match within each row and be `cm`, `mm` or `in`. All four readings must be positive finite decimal numbers. Care codes are `wash`, `dry`, `wash-and-dry`, `rinse`, `steam`, `press` or `other`; they describe what was done, not recommended care. **Leave notes empty** and keep detailed care observations in your own records. Use `yes` for area only when the paired length and width readings describe actual flat rectangles; otherwise use `no` or leave blank.

Do not include names, contact details, body measurements, personal identifiers or other sensitive information. The package makes no network requests, adds no analytics and does not cache or log CSV contents. It reads only the selected input and writes the explicitly selected outputs. Ordinary terminal history, pipes, filesystem permissions and other software on the device remain outside its control.

Malformed quoting, encoding or a policy/limit violation rejects the entire submission before calculation. Numerical, unit and column-count problems produce per-record diagnostics while other valid records remain separate. This distinction is deliberate.

## API and results

```python
from sewlore_fabric_care import (
    BLANK_CSV, convert_length, validate_submission,
    export_validated, export_errors,
)

assert convert_length(0.625, "in", "mm") == 15.875
accepted, corrections = validate_submission(BLANK_CSV.encode("utf-8"))
accepted_csv = export_validated(accepted)
corrections_csv = export_errors(corrections)
```

`calculate_changes(before_length_mm, before_width_mm, after_length_mm, after_width_mm, rectangle_assumption=False)` returns signed contraction percentages. For each axis, `(before - after) / before * 100` is positive for contraction and negative for expansion. Optional rectangular-area contraction is `100 * (1 - after_length / before_length * after_width / before_width)`. It is `None` without the explicit rectangle assumption. Area percentages are not added across axes.

The labelled hypothetical input 20 × 20 cm becoming 19 × 19.5 cm gives approximately +5%, +2.5% and +7.375% rectangular-area contraction. No fabric was tested for these values. Calculations do not certify measurement precision, material performance, future care cycles or garment fit. Binary floating-point arithmetic is used; exported finite numbers use up to 12 significant digits. Preserve original readings for later review.

The lower-level `validate_csv(str)` is also available. It permits free-text notes and generic sample identifiers and uses a one-million-character limit. **It does not enforce the strict CLI policy.** Choose `validate_submission` for hosted-compatible anonymous records. CSV exporters quote fields and prefix formula-like text with an apostrophe; genuine numeric negatives remain numeric. Check your spreadsheet import settings.

## Documentation, building and checks

Sphinx documentation is in `docs/`; `.readthedocs.yaml` builds it with Python 3.12. The documentation build needs the optional tooling; normal use needs no third-party libraries.

```sh
python -m pip install --index-url https://pypi.org/simple -r requirements-build.txt
python -m build
python -m pip install --force-reinstall --no-deps dist/sewlore_fabric_care-0.1.0-py3-none-any.whl
python -B -m unittest discover -s tests -v
python -m sphinx -W --keep-going -b html docs _build/html
```

Checks exercise the installed API, console entrypoint, file/stdin exports, exit codes, malformed and rejected inputs, unit handling, quoted CSV and overwrite protection. They use invented inputs. See [CSV recording context](https://sewlore-preparation-notes.blogspot.com/2026/10/what-to-record-before-cutting-fabric.html) and the [browser-local shrinkage calculator](https://sewlore-fabric-shrinkage.web.app/) for complementary workflows.

## Source, provenance and licence

The calculation core comes unchanged from the [Fabric-Care CSV Validator v1.0.0 release](https://github.com/gokimedia/sewlore-fabric-care-validator/releases/tag/v1.0.0), commit `1db7b9a4fc8da8a109d6b40e125387752583c8bb`. Its input policy changes only the import to a package-relative path. Distribution version **0.1.0** adds the API packaging, local CLI and documentation; it is distinct from that original software version. The [original source repository](https://github.com/gokimedia/sewlore-fabric-care-validator) and its software DOI identify the original release, not a DOI assigned to this new distribution.

Original code and documentation © 2026 Sewlore, MIT licence in `LICENSE.txt`, for any applicable copyright. Development and documentation were AI-assisted with OpenAI Codex. No individual author, academic affiliation, laboratory study, physical measurement dataset, peer review or human visual review is claimed. The licence grants no trademark ownership or platform endorsement.

[Sewlore](https://sewlore.com/) — Recording the method beside the measurement.
