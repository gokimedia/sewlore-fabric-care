"""Sphinx configuration. No external extensions or hosted services required."""
project = "Sewlore Fabric Care"
author = "Sewlore"
copyright = "2026, Sewlore"
version = release = "0.1.0"
extensions = ["sphinx.ext.autodoc"]
html_theme = "alabaster"
html_title = "Sewlore Fabric Care: local CSV validation"
exclude_patterns = ["_build"]
nitpicky = True
autodoc_member_order = "bysource"
