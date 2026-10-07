Sewlore Fabric Care
===================

Check paired fabric-care readings locally before comparing them. This
dependency-free Python package provides a bounded anonymous-record validator,
separate accepted and correction exports, and a command-line interface.
The initial template has no sample rows. All examples are hypothetical software
inputs; no fabric testing or garment-fit result is claimed.

Install the `published Python version 0.1.0 <https://pypi.org/project/sewlore-fabric-care/0.1.0/>`_
with ``python -m pip install sewlore-fabric-care==0.1.0``. This documentation
is built from the `distribution source repository <https://github.com/gokimedia/sewlore-fabric-care>`_.

Choose the appropriate tool
----------------------------

* Use this Python API/CLI for multiple paired fabric-care records, anonymous
  CSV checks and separate accepted/correction exports. Its ``convert_length``
  accepts positive finite lengths in ``cm``, ``mm`` or ``in``.
* Use the `browser-local shrinkage calculator <https://sewlore-fabric-shrinkage.web.app/>`_
  for one paired length/width comparison, with optional rectangular area.
* Use `Sewlore Sewing Math on npm <https://www.npmjs.com/package/@sewingselami/sewlore-sewing-math>`_
  for JavaScript stretch/recovery and print-scale comparisons. Those calculations
  require positive plain lengths in one consistent unit. Its ``convertLength``
  helper supports only ``cm``/``in`` and allows signed finite inputs, including
  zero; it is not the Python converter's input contract. It does not provide
  whole-file CSV validation or fabric-care area calculations.

The Python package does not calculate stretch/recovery or PDF print errors.

For the recording method, units and interpretation, read Sewlore's
`Fabric Measurement Guide: Stretch, Recovery and Care <https://sewlore.com/pages/fabric-measurement-methods-guide>`_.
The `interactive validator <https://sewlore-fabric-care-validator.streamlit.app/>`_
is a separate hosted interface; this package does not contact it.

.. toctree::
   :maxdepth: 2

   quickstart
   csv-policy
   api
   reproducibility

Code and educational documentation are MIT licensed for any applicable
copyright, Copyright (c) 2026 Sewlore. Development and documentation were
AI-assisted with OpenAI Codex. No peer review or individual academic authorship
is claimed. See the included LICENSE.txt for the full notice.
