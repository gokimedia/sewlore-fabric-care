Install and use the CLI
=======================

Use Python 3.10 or later. Checks use Python 3.12. Install the
`published version 0.1.0 <https://pypi.org/project/sewlore-fabric-care/0.1.0/>`_
from PyPI. There are no runtime dependencies.

.. code-block:: console

   python -m pip install sewlore-fabric-care==0.1.0
   sewlore-fabric-care template --output blank.csv
   sewlore-fabric-care validate readings.csv --accepted accepted.csv --corrections corrections.csv

The template is header-only. Record your own readings before validation;
do not treat the invented example file as care data. The command can also be
invoked as ``python -m sewlore_fabric_care``.

Fill ``blank.csv`` with your own anonymous records and save that completed file
as ``readings.csv`` for the command above. Preserve the ten-column header and
leave notes empty. See :doc:`csv-policy` before entering records. The command
does not infer care settings or supply missing physical readings.

For deliberate development from the
`source repository <https://github.com/gokimedia/sewlore-fabric-care>`_,
``python -m pip install .`` installs the checked-out revision instead.

Input and output choices
------------------------

``-`` reads input from stdin or sends one chosen CSV to stdout. Both output
destinations are required. Stdout contains only CSV; count summaries go to
stderr. No CSV contents are logged.

.. code-block:: console

   sewlore-fabric-care template
   sewlore-fabric-care validate - --accepted - --corrections corrections.csv

The input is read in a bounded operation, at most 128 KiB plus one byte to
detect an oversized submission. Existing output files are refused without
``--overwrite``. Input and output files must differ; this protection also applies
with ``--overwrite``. Parent directories must already exist. File writing is
not a multi-file transaction: an I/O failure during writing can leave partial
output, which must be checked before reuse.

Exit codes
----------

* ``0``: no correction entries; a valid header-only file also returns zero.
* ``1``: correction entries were exported, separately from any accepted records.
* ``2``: usage, path or I/O error; outputs may be absent or partial.

Privacy and storage
-------------------

Keep records anonymous. The tool makes no network requests, adds no analytics,
and uses no data cache. The only persistent outputs are the files the user
explicitly requests. Terminal history, other software and filesystem access
are outside its control. The
`recording guide <https://sewlore-preparation-notes.blogspot.com/2026/10/what-to-record-before-cutting-fabric.html>`_
explains which method details to retain separately in private records.
