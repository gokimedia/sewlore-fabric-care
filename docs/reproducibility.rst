Version, source and reproducibility
========================================

Distribution version 0.1.0 packages the calculation core from the original
`Fabric-Care CSV Validator v1.0.0 <https://github.com/gokimedia/sewlore-fabric-care-validator/releases/tag/v1.0.0>`_,
commit ``1db7b9a4fc8da8a109d6b40e125387752583c8bb``. The core is unchanged;
the input policy changes one import to a package-relative path. This
distribution adds a local CLI, an installable API and these documents.
Its version and source archive are separate from the original release.

The `PyPI 0.1.0 files <https://pypi.org/project/sewlore-fabric-care/0.1.0/>`_
were built and published from distribution-source commit
``5eb88ca82ec4f9536447ac68fe27482d56de3e27``. The
`live repository <https://github.com/gokimedia/sewlore-fabric-care>`_
and `latest Read the Docs edition <https://sewlore-fabric-care.readthedocs.io/en/latest/>`_
can receive documentation and project-link updates after that upload.
These updates do not replace the published version's files or claim that its
embedded metadata has changed. Record the installed version and source revision
you actually use.

The original software is preserved as
`DOI 10.5281/zenodo.23193335 <https://doi.org/10.5281/zenodo.23193335>`_.
That DOI identifies the original software archive, not a new DOI for this
distribution or an educational paper. It remains the reference for the
archived v1.0.0 source, separate from this distribution.

Retain the distribution version, Python version, source readings, units,
rectangle assumption and original method notes when comparing results.
Calculations use binary floating point, and CSV numeric formatting uses up to
12 significant digits. Results describe entered readings, not material testing,
fit, certified accuracy or future care behaviour.

Checks and documentation build
------------------------------

.. code-block:: console

   python -m pip install --index-url https://pypi.org/simple -r requirements-build.txt
   python -m build
   python -m pip install --force-reinstall --no-deps dist/sewlore_fabric_care-0.1.0-py3-none-any.whl
   python -B -m unittest discover -s tests -v
   python -m sphinx -W --keep-going -b html docs _build/html

The suite uses hypothetical software fixtures to check installed imports,
the console entrypoint, file/stdin handling, exports, policy errors and file
protection. No physical measurements are supplied. Sphinx is documentation
tooling only; its pinned version requires Python 3.12. Read the Docs uses
Python 3.12 in the supplied configuration. A local docs build proves local
generation, not deployment on that external service.

Licence and provenance
----------------------

Code and original documentation are distributed under MIT for any applicable
copyright, Copyright (c) 2026 Sewlore. Keep the full LICENSE.txt notice when
redistributing. Names and branding do not confer trademark rights or platform
endorsement. Development and documentation were AI-assisted with OpenAI Codex;
no individual author, academic affiliation, physical measurement dataset,
laboratory study, peer review or human visual review is claimed.

`Sewlore <https://sewlore.com/>`_ publishes the accompanying measurement guide.
