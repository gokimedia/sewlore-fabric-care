"""Explicit local file/stdin interface; no network, telemetry or server."""
import argparse
from contextlib import ExitStack
from pathlib import Path
import sys

from . import __version__
from .input_policy import MAX_BYTES, validate_submission
from .validator import BLANK_CSV, export_errors, export_validated


def _parser():
    parser = argparse.ArgumentParser(
        prog="sewlore-fabric-care",
        description="Validate anonymous fabric-care CSV locally, with separate exports.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)
    template = subcommands.add_parser("template", help="Write the exact header, without sample rows.")
    template.add_argument("--output", default="-", metavar="PATH", help="UTF-8 file, or - for stdout (default).")
    template.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing an output file.")
    validate = subcommands.add_parser("validate", help="Apply the bounded anonymous-record policy.")
    validate.add_argument("input", nargs="?", default="-", metavar="INPUT", help="UTF-8 CSV file, or - for stdin (default).")
    validate.add_argument("--accepted", required=True, metavar="PATH", help="Accepted CSV destination, or - for stdout.")
    validate.add_argument("--corrections", required=True, metavar="PATH", help="Corrections CSV destination, or - for stdout.")
    validate.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing output files; never the input.")
    return parser


def _check_destinations(destinations, overwrite, input_path=None):
    if sum(path == "-" for path in destinations) > 1:
        raise ValueError("Only one CSV destination may use stdout.")
    resolved = [Path(path).resolve() for path in destinations if path != "-"]
    if len(resolved) != len(set(resolved)):
        raise ValueError("Accepted and correction destinations must be different files.")
    if input_path is not None and input_path in resolved:
        raise ValueError("An output destination must not replace the input file.")
    for index, path in enumerate(resolved):
        if path.exists():
            if input_path is not None and input_path.exists() and path.samefile(input_path):
                raise ValueError("An output destination must not replace the input file.")
            if any(other.exists() and path.samefile(other) for other in resolved[:index]):
                raise ValueError("Accepted and correction destinations must be different files.")
        if not overwrite and path.exists():
            raise ValueError("An output file already exists; choose another path or use --overwrite.")
        if not path.parent.is_dir():
            raise ValueError("An output parent directory does not exist.")
        if path.is_dir():
            raise ValueError("An output destination is a directory.")


def _write_outputs(outputs, overwrite):
    # Open every file before writing data. Exclusive creation also protects
    # against an output being created between the preflight and this step.
    created = []
    writing_started = False
    try:
        with ExitStack() as stack:
            handles = []
            for destination, text in outputs:
                if destination == "-":
                    handle = sys.stdout.buffer
                else:
                    handle = stack.enter_context(open(destination, "wb" if overwrite else "xb"))
                    if not overwrite:
                        created.append(Path(destination))
                handles.append((handle, text.encode("utf-8")))
            writing_started = True
            for handle, data in handles:
                handle.write(data)
                handle.flush()
    except OSError:
        # Only remove files this invocation exclusively created, before data
        # writing began. An I/O failure during writing may leave partial output.
        if not writing_started:
            for path in created:
                try:
                    path.unlink()
                except OSError:
                    pass
        raise


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.command == "template":
            _check_destinations([args.output], args.overwrite)
            _write_outputs([(args.output, BLANK_CSV)], args.overwrite)
            return 0
        input_path = None if args.input == "-" else Path(args.input).resolve()
        _check_destinations([args.accepted, args.corrections], args.overwrite, input_path)
        if args.input == "-":
            data = sys.stdin.buffer.read(MAX_BYTES + 1)
        else:
            with open(input_path, "rb") as handle:
                data = handle.read(MAX_BYTES + 1)
        accepted, corrections = validate_submission(data)
        _write_outputs([
            (args.accepted, export_validated(accepted)),
            (args.corrections, export_errors(corrections)),
        ], args.overwrite)
        print(f"Accepted records: {len(accepted)}; correction entries: {len(corrections)}.", file=sys.stderr)
        return 1 if corrections else 0
    except (OSError, ValueError):
        print("File I/O or destination error. Check paths, permissions and output options; input contents are not logged.", file=sys.stderr)
        return 2
