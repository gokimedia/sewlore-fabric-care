"""Installed API/CLI checks. Every numeric fixture is hypothetical software input."""
import csv
import importlib.metadata
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sewlore_fabric_care import (
    BLANK_CSV, ERROR_COLUMNS, INPUT_COLUMNS, MAX_BYTES, MAX_RECORDS,
    OUTPUT_COLUMNS, __version__, calculate_changes, convert_length,
    export_validated, validate_csv, validate_submission,
)

HERE = Path(__file__).resolve().parents[1]


def fixture(**changes):
    values = ["sample-001", "cm", "cm", "20", "20", "19", "19.5", "wash", "yes", ""]
    row = dict(zip(INPUT_COLUMNS, values))
    row.update(changes)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(INPUT_COLUMNS)
    writer.writerow([row[key] for key in INPUT_COLUMNS])
    return buffer.getvalue().encode("utf-8")


def parsed(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"), newline="")))


class InstalledDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def command(self, *arguments, input_bytes=None):
        return subprocess.run(
            [sys.executable, "-B", "-m", "sewlore_fabric_care", *arguments],
            input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.directory, check=False,
        )

    def validate(self, data, **kwargs):
        result = self.command(
            "validate", "-", "--accepted", "accepted.csv",
            "--corrections", "corrections.csv", input_bytes=data, **kwargs,
        )
        accepted = self.directory / "accepted.csv"
        corrections = self.directory / "corrections.csv"
        return result, parsed(accepted.read_bytes()), parsed(corrections.read_bytes())

    def test_installed_metadata_and_console_entrypoint(self):
        self.assertEqual(importlib.metadata.version("sewlore-fabric-care"), __version__)
        requirements = importlib.metadata.requires("sewlore-fabric-care") or []
        self.assertTrue(all('extra == "docs"' in value for value in requirements))
        entrypoint = next(
            entry for entry in importlib.metadata.distribution("sewlore-fabric-care").entry_points
            if entry.group == "console_scripts" and entry.name == "sewlore-fabric-care"
        )
        self.assertEqual(entrypoint.value, "sewlore_fabric_care.cli:main")
        executable = Path(sys.executable).parent / ("sewlore-fabric-care.exe" if sys.platform == "win32" else "sewlore-fabric-care")
        result = subprocess.run([str(executable), "--version"], capture_output=True, cwd=self.directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), b"sewlore-fabric-care 0.1.0")

    def test_template_stdout_is_header_only(self):
        result = self.command("template")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, BLANK_CSV.encode())
        self.assertEqual(result.stderr, b"")

    def test_template_file_and_explicit_overwrite(self):
        destination = self.directory / "blank.csv"
        result = self.command("template", "--output", str(destination))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(destination.read_bytes(), BLANK_CSV.encode())
        destination.write_bytes(b"keep this file")
        self.assertEqual(self.command("template", "--output", str(destination)).returncode, 2)
        self.assertEqual(destination.read_bytes(), b"keep this file")
        self.assertEqual(self.command("template", "--output", str(destination), "--overwrite").returncode, 0)
        self.assertEqual(destination.read_bytes(), BLANK_CSV.encode())

    def test_valid_stdin_writes_two_distinct_headers_and_signed_results(self):
        result, accepted, corrections = self.validate(fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tuple(accepted[0]), OUTPUT_COLUMNS)
        self.assertEqual(float(accepted[0]["length_change_percent"]), 5)
        self.assertEqual(float(accepted[0]["width_change_percent"]), 2.5)
        self.assertEqual(float(accepted[0]["rectangular_area_change_percent"]), 7.375)
        self.assertEqual(corrections, [])
        correction_header = next(csv.reader(io.StringIO((self.directory / "corrections.csv").read_text())))
        self.assertEqual(tuple(correction_header), ERROR_COLUMNS)
        self.assertIn(b"Accepted records: 1; correction entries: 0.", result.stderr)
        self.assertEqual(result.stdout, b"")

    def test_file_input_hypothetical_demo_keeps_two_records_and_one_correction(self):
        source = self.directory / "hypothetical.csv"
        source.write_bytes((HERE / "examples/demo-hypothetical.csv").read_bytes())
        result = self.command("validate", str(source), "--accepted", "accepted.csv", "--corrections", "corrections.csv")
        self.assertEqual(result.returncode, 1, result.stderr)
        accepted = parsed((self.directory / "accepted.csv").read_bytes())
        corrections = parsed((self.directory / "corrections.csv").read_bytes())
        self.assertEqual([row["sample_id"] for row in accepted], ["sample-001", "sample-003"])
        self.assertEqual(corrections[0]["sample_id"], "sample-002")
        self.assertEqual(corrections[0]["field"], "units")
        self.assertEqual(float(accepted[1]["length_change_percent"]), -5)
        self.assertEqual(accepted[1]["rectangular_area_change_percent"], "")

    def test_one_stdout_destination_contains_csv_without_count_summary(self):
        result = self.command("validate", "-", "--accepted", "-", "--corrections", "corrections.csv", input_bytes=fixture())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(parsed(result.stdout)), 1)
        self.assertNotIn(b"Accepted records:", result.stdout)
        self.assertIn(b"Accepted records:", result.stderr)

    def test_header_only_returns_success_with_empty_exports(self):
        result, accepted, corrections = self.validate(BLANK_CSV.encode())
        self.assertEqual((result.returncode, accepted, corrections), (0, [], []))

    def test_malformed_quoted_csv_rejects_before_valid_row_calculations(self):
        result, accepted, corrections = self.validate(fixture() + b'"unterminated\n')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(accepted, [])
        self.assertEqual(corrections[0]["field"], "CSV")

    def test_policy_violation_rejects_all_and_redacts_rejected_text(self):
        bad = fixture(sample_id="not-an-anonymous-code", notes="=1+1", care_method="invented free text").split(b"\n", 1)[1]
        result, accepted, corrections = self.validate(fixture() + bad)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(accepted, [])
        self.assertEqual({row["field"] for row in corrections}, {"sample_id", "notes", "care_method"})
        exported = (self.directory / "corrections.csv").read_bytes()
        for text in (b"not-an-anonymous-code", b"=1+1", b"invented free text"):
            self.assertNotIn(text, exported + result.stderr)

    def test_column_count_error_keeps_other_valid_record(self):
        result, accepted, corrections = self.validate(fixture() + b"sample-002,cm\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(accepted), 1)
        self.assertEqual(corrections[0]["field"], "columns")

    def test_invalid_numeric_records_report_corrections_not_cli_crashes(self):
        for reading in ("0", "-1", "NaN", "Infinity", "1e309", "1e308"):
            with self.subTest(reading=reading):
                result = self.command("validate", "-", "--accepted", "-", "--corrections", "numeric-errors.csv", "--overwrite", input_bytes=fixture(before_length=reading))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(parsed(result.stdout), [])
                self.assertEqual(parsed((self.directory / "numeric-errors.csv").read_bytes())[0]["field"], "before_length")

    def test_cm_mm_in_pairs_have_same_percentages_and_inconsistent_pair_is_rejected(self):
        fixtures = [
            fixture(before_unit="cm", after_unit="cm"),
            fixture(before_unit="mm", after_unit="mm", before_length="200", before_width="200", after_length="190", after_width="195"),
            fixture(before_unit="in", after_unit="in", before_length="8", before_width="8", after_length="7.6", after_width="7.8"),
        ]
        for data in fixtures:
            records, errors = validate_submission(data)
            self.assertEqual(errors, [])
            self.assertAlmostEqual(records[0]["length_change_percent"], 5)
            self.assertAlmostEqual(records[0]["width_change_percent"], 2.5)
            self.assertAlmostEqual(records[0]["rectangular_area_change_percent"], 7.375)
        records, errors = validate_submission(fixture(after_unit="mm"))
        self.assertEqual(records, [])
        self.assertIn("units", {row["field"] for row in errors})

    def test_oversized_stdin_and_row_limit_have_bounded_diagnostics(self):
        result = self.command("validate", "-", "--accepted", "-", "--corrections", "size.csv", input_bytes=b"x" * (MAX_BYTES + 1))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(parsed((self.directory / "size.csv").read_bytes())[0]["field"], "file size")
        row = fixture().split(b"\n", 1)[1]
        result = self.command("validate", "-", "--accepted", "-", "--corrections", "rows.csv", input_bytes=BLANK_CSV.encode() + row * (MAX_RECORDS + 1))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(parsed((self.directory / "rows.csv").read_bytes())[0]["field"], "record limit")

    def test_utf8_bom_accepted_and_invalid_encoding_rejected(self):
        result, accepted, corrections = self.validate(b"\xef\xbb\xbf" + fixture())
        self.assertEqual((result.returncode, len(accepted), corrections), (0, 1, []))
        result = self.command("validate", "-", "--accepted", "-", "--corrections", "encoding.csv", input_bytes=b"\xff")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(parsed((self.directory / "encoding.csv").read_bytes())[0]["field"], "encoding")

    def test_wrong_header_is_reported(self):
        result, accepted, corrections = self.validate(b"different,header\n")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(accepted, [])
        self.assertEqual(corrections[0]["field"], "header")

    def test_duplicate_destinations_and_two_stdout_destinations_are_refused(self):
        for accepted, corrections in (("same.csv", "same.csv"), ("-", "-")):
            result = self.command("validate", "-", "--accepted", accepted, "--corrections", corrections, input_bytes=fixture())
            self.assertEqual(result.returncode, 2)
            self.assertFalse((self.directory / "same.csv").exists())
            self.assertEqual(result.stdout, b"")

    def test_input_cannot_be_overwritten_even_with_permission(self):
        source = self.directory / "source.csv"
        source.write_bytes(fixture())
        result = self.command("validate", str(source), "--accepted", str(source), "--corrections", "corrections.csv", "--overwrite")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(source.read_bytes(), fixture())
        self.assertFalse((self.directory / "corrections.csv").exists())

    def test_existing_second_destination_prevents_first_file_creation(self):
        corrections = self.directory / "corrections.csv"
        corrections.write_bytes(b"retain")
        result = self.command("validate", "-", "--accepted", "accepted.csv", "--corrections", str(corrections), input_bytes=fixture())
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.directory / "accepted.csv").exists())
        self.assertEqual(corrections.read_bytes(), b"retain")

    def test_hard_link_to_input_is_also_refused_with_overwrite(self):
        source = self.directory / "source.csv"
        source.write_bytes(fixture())
        alias = self.directory / "alias.csv"
        try:
            alias.hardlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("This filesystem does not support the hard-link fixture.")
        result = self.command("validate", str(source), "--accepted", str(alias), "--corrections", "corrections.csv", "--overwrite")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(source.read_bytes(), fixture())
        self.assertFalse((self.directory / "corrections.csv").exists())

    def test_two_hard_linked_outputs_are_refused_with_overwrite(self):
        accepted = self.directory / "accepted.csv"
        accepted.write_bytes(b"retain")
        corrections = self.directory / "corrections.csv"
        try:
            corrections.hardlink_to(accepted)
        except (OSError, NotImplementedError):
            self.skipTest("This filesystem does not support the hard-link fixture.")
        result = self.command("validate", "-", "--accepted", str(accepted), "--corrections", str(corrections), "--overwrite", input_bytes=fixture())
        self.assertEqual(result.returncode, 2)
        self.assertEqual(accepted.read_bytes(), b"retain")
        self.assertEqual(corrections.read_bytes(), b"retain")

    def test_missing_input_is_io_error_without_exports(self):
        result = self.command("validate", "missing.csv", "--accepted", "accepted.csv", "--corrections", "corrections.csv")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.directory / "accepted.csv").exists())
        self.assertFalse((self.directory / "corrections.csv").exists())

    def test_installed_api_unit_conversion_expansion_and_optional_area(self):
        self.assertEqual(convert_length(0.625, "in", "mm"), 15.875)
        self.assertEqual(convert_length(15.875, "mm", "cm"), 1.5875)
        self.assertAlmostEqual(calculate_changes(100, 100, 110, 100)["length_change_percent"], -10)
        self.assertIsNone(calculate_changes(100, 100, 110, 100)["rectangular_area_change_percent"])

    def test_generic_api_csv_escaping_and_numeric_negatives_are_distinct_from_strict_policy(self):
        notes = '=SUM(1,2)\n"quoted"'
        records, errors = validate_csv(fixture(after_length="21", notes=notes).decode())
        self.assertEqual(errors, [])
        exported = export_validated(records)
        row = parsed(exported.encode())[0]
        self.assertEqual(row["notes"], "'" + notes)
        self.assertEqual(row["length_change_percent"], "-5")
        self.assertEqual(float(row["length_change_percent"]), -5)
        self.assertEqual(validate_submission(fixture(notes=notes))[0], [])


if __name__ == "__main__":
    unittest.main()
