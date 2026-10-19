#!/usr/bin/env python3
"""Run from the project root: python3 tools/import_chart.py [path/to/song.chart]."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

try:
    from .chart_importer import InvalidChart, compatibility, cpp_assets, diagnostic, normalize
except ImportError:
    from chart_importer import InvalidChart, compatibility, cpp_assets, diagnostic, normalize

ROOT = Path(__file__).resolve().parents[1]


def save_text(path, text):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def import_file(source, output_root):
    if source.stem in ("", ".", ".."):
        raise OSError("Rename the chart to a normal filename such as my_song.chart.")
    destination = output_root / source.stem
    destination.mkdir(parents=True, exist_ok=True)
    diagnostics = []
    report = dict(schema_version="gba-chart-import-report-v1", source_name=source.name,
                  valid=False, status="invalid", assets_generated=False,
                  playable_now=False, tracks=[], diagnostics=diagnostics)
    try:
        if source.suffix.lower() != ".chart":
            raise InvalidChart("WRONG_EXTENSION", "Only .chart files are read; audio/MIDI import is not supported.")
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        report["source_sha256"] = digest
        text = data.decode("utf-8-sig")
        song = normalize(text, source.name, diagnostics)
        song["source_sha256"] = digest
        if source.with_name("song.ini").exists():
            diagnostic(diagnostics, "SIDECAR_INI_NOT_APPLIED", "song.ini exists beside this chart. Its metadata/delay overrides are not applied; verify them before audio pairing.")
        report["tracks"] = compatibility(song, diagnostics)
        report["metadata"] = song["metadata"]
        report["available_difficulties"] = [track["difficulty"] for track in report["tracks"] if track["prepared"]]
        report.update(valid=True, status="prepared_not_playable", assets_generated=True,
                      planned_layouts=dict(Easy=["Left", "A", "B"], Medium=["Left", "Right", "A", "B"],
                                           Hard=["Left", "Up", "Right", "A", "B"]),
                      tempo_point_count=len(song["tempo_map"]),
                      tempo_change_count=len(song["tempo_map"]) - 1,
                      resolution=song["resolution"], timing=song["timing"])
        save_text(destination / "song.json", json.dumps(song, indent=2, ensure_ascii=False) + "\n")
        save_text(destination / "song_data.hpp", cpp_assets(song, digest))
    except InvalidChart as error:
        diagnostic(diagnostics, error.code, str(error), error.line, "error")
    except (OSError, UnicodeError) as error:
        diagnostic(diagnostics, "READ_OR_WRITE_ERROR", str(error), severity="error")
    except ValueError as error:
        diagnostic(diagnostics, "DATA_LIMIT", f"Numeric data could not be represented: {error}", severity="error")
    if any(item["severity"] == "error" for item in diagnostics):
        report.update(valid=False, status="invalid", assets_generated=False)
        # This dedicated directory manages only these named generated assets.
        # Do not leave an old valid header behind after a failed re-import.
        for name in ("song.json", "song_data.hpp"):
            (destination / name).unlink(missing_ok=True)
    save_text(destination / "report.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    lines = [f"Chart: {source.name}", f"Result: {report['status']}",
             "New imported data connected to ROM: NO (working original demo unchanged)", ""]
    if report["valid"]:
        metadata = report["metadata"]
        lines.extend([f"Title: {metadata.get('Name', '(not supplied)')}",
                      f"Artist: {metadata.get('Artist', '(not supplied)')}",
                      f"Resolution: {report['resolution']}; tempo points: {report['tempo_point_count']}",
                      f"Chart Offset: {metadata.get('Offset', '0 (implicit)')} seconds; added to chart time at the audio origin.", ""])
    for track in report["tracks"]:
        state = "prepared" if track["prepared"] else "empty (not prepared)"
        lines.append(f"  {track['section']}: {track['note_count']} notes, {track['fret_slots_required']} fret slots, "
                     f"{track['chord_count']} chords, {track['sustain_count']} sustains; {state}, not playable")
    for item in diagnostics:
        location = f" (line {item['line']})" if item["line"] else ""
        lines.append(f"{item['severity'].upper()} {item['code']}{location}: {item['message']}")
    save_text(destination / "report.txt", "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nReport folder: {destination}\n")
    return report["valid"]


def main():
    parser = argparse.ArgumentParser(description="Inspect and prepare .chart data; never replaces the live game's chart/audio.")
    parser.add_argument("chart", nargs="?", type=Path, help="One UTF-8 .chart file; omit to import imports/incoming/*.chart")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "imports/output", help="Managed output root; one subfolder per chart stem")
    args = parser.parse_args()
    if args.chart:
        sources = [args.chart]
    else:
        sources = sorted(p for p in (ROOT / "imports/incoming").iterdir() if p.is_file() and p.suffix.lower() == ".chart")
    if not sources:
        parser.error("Place a licensed .chart file in imports/incoming, or supply a path. No files imported.")
    valid = True
    for source in sources:
        try:
            valid = import_file(source, args.output_dir) and valid
        except OSError as error:
            print(f"ERROR: cannot write report for {source.name}: {error}", file=sys.stderr)
            valid = False
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
