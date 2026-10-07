Python API
==========

Import the supported functions from ``sewlore_fabric_care``. The calculation
core uses ordinary floating-point values and raises ``ValueError`` for
unsupported units, non-positive readings or results outside representable
numeric limits. In particular, very large or very small finite readings may
still produce an unrepresentable conversion or ratio.

This is the Python fabric-care API. The separate
`JavaScript Sewing Math package <https://www.npmjs.com/package/@sewingselami/sewlore-sewing-math>`_
handles stretch/recovery and print-scale comparison. Its unit conversion
supports only ``cm``/``in`` and signed finite inputs, including zero, while
Python ``convert_length`` supports ``cm``/``mm``/``in`` and requires a positive
length. The JavaScript stretch/print functions still require positive lengths.
Do not substitute either conversion contract for the other.

Bounded submission
------------------

.. autofunction:: sewlore_fabric_care.validate_submission

Return value: ``(accepted_records, correction_entries)``. It accepts bytes;
other types raise ``TypeError``. The strict policy is described in
:doc:`csv-policy`. Neither validation nor exports write a file automatically.

.. code-block:: python

   from sewlore_fabric_care import BLANK_CSV, validate_submission
   accepted, corrections = validate_submission(BLANK_CSV.encode("utf-8"))
   assert accepted == [] and corrections == []

Units and signed change
------------------------

.. autofunction:: sewlore_fabric_care.convert_length

Supported units are ``cm``, ``mm`` and ``in``; exactly one inch equals 25.4 mm.
Input and output lengths must be positive and finite.

.. autofunction:: sewlore_fabric_care.calculate_changes

The four arguments describe before/after length and width in millimetres.
Using another common unit for all four inputs gives the same ratios, but
converting to millimetres keeps the API contract explicit.

For each axis, signed contraction is
``100 * (1 - after / before)``. Positive means contraction; negative means
expansion. With ``rectangle_assumption=True``, area contraction is
``100 * (1 - after_length / before_length * after_width / before_width)``.
Without that explicit boolean, the area value is ``None``. Axis percentages
must not be added. This model assumes paired flat rectangles and does not
account for irregular edges or measurement uncertainty.

.. code-block:: python

   from sewlore_fabric_care import calculate_changes, convert_length
   # Hypothetical software inputs, not measurements of fabric.
   changes = calculate_changes(200, 200, 190, 195, rectangle_assumption=True)
   # Approximately +5%, +2.5%, and +7.375% rectangular-area contraction.
   length_mm = convert_length(0.625, "in", "mm")  # 15.875

The `browser-local calculator <https://sewlore-fabric-shrinkage.web.app/>`_
provides a separate single-pair interface for the same interpretation.

Exports and lower-level API
---------------------------

.. autofunction:: sewlore_fabric_care.export_validated

.. autofunction:: sewlore_fabric_care.export_errors

Both return CSV text. See :doc:`csv-policy` for columns and spreadsheet handling.

.. autofunction:: sewlore_fabric_care.validate_csv

This lower-level API accepts text, generic identifiers and free-text notes,
and has a one-million-character limit. **It does not implement the strict
anonymous submission policy.** Use ``validate_submission`` when matching the
CLI/hosted restrictions is required.
