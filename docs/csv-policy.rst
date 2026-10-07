CSV schema and strict policy
============================

``validate_submission`` and the CLI accept UTF-8 bytes, with optional BOM,
up to 128 KiB and 250 non-empty records. The supplied ten-column header must
appear once and in this order:

.. code-block:: text

   sample_id,before_unit,after_unit,before_length,before_width,after_length,after_width,care_method,rectangle_assumption,notes

.. list-table:: Input fields
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Required meaning
   * - ``sample_id``
     - ``sample-`` plus 1–6 digits. No identifiers for people.
   * - ``before_unit``, ``after_unit``
     - Matching ``cm``, ``mm`` or ``in`` within each row.
   * - Four length/width readings
     - Finite decimal numbers greater than zero; no unit text or thousands separators.
   * - ``care_method``
     - ``wash``, ``dry``, ``wash-and-dry``, ``rinse``, ``steam``, ``press`` or ``other``.
   * - ``rectangle_assumption``
     - ``yes`` only for actual flat rectangles; otherwise ``no`` or blank.
   * - ``notes``
     - Empty. Keep detailed care notes in your own private records.

Care codes describe an action the user actually performed; they prescribe no
care procedure. Follow the material manufacturer's care instructions and record
the method separately. Do not submit body measurements or other sensitive data.

Rejection versus per-record corrections
---------------------------------------

Encoding, malformed quoting, a wrong header, byte/row limits or any anonymous
policy violation rejects the entire submission before calculation. Such a
result still has a correction export and an accepted export containing only
its header. Unrecognized identifiers are redacted from diagnostics.

After these checks, invalid numeric readings, mismatched units and inconsistent
column counts receive per-record correction entries; other valid records remain
in the separate accepted output. An error entry is not a sample count: one row
may produce multiple entries. Blank lines are ignored; partially empty records
are not. Record numbers refer to logical CSV records, with the header as 1, so
quoted multiline content does not have the same numbering as physical lines.

Exports
-------

Accepted exports append ``length_change_percent``, ``width_change_percent`` and
``rectangular_area_change_percent``. Corrections contain ``record_number``,
``sample_id``, ``field`` and ``message``. No rectangle assumption means an empty
area field. Finite numeric outputs use up to 12 significant digits; retain
source readings rather than treating the export as a precision guarantee.

All cells are quoted. Formula-like text receives a leading apostrophe; genuine
numeric negative values remain numbers. This reduces a common spreadsheet
import risk but does not certify every spreadsheet configuration. Inspect
import settings before using exports in another application.
