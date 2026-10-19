#!/usr/bin/env python3
"""Inspect an authorized Clone Hero package without changing the demo ROM."""
import argparse
import configparser
import json
from pathlib import Path
import sys
import zipfile

try:
    from .chart_importer import InvalidChart, diagnostic
    from .import_chart import save_text
    from .song_package import inspect
except ImportError:
    from chart_importer import InvalidChart, diagnostic
    from import_chart import save_text
    from song_package import inspect

ROOT = Path(__file__).resolve().parents[1]


def import_song(source, output_root, chart=None, audio=None, offset_policy=None):
    if source.stem in ("", ".", ".."):
        raise OSError("Choose a named song folder/file, not a filesystem root.")
    destination = output_root / source.stem
    destination.mkdir(parents=True, exist_ok=True)
    diagnostics = []
    report = dict(schema_version="gba-song-package-report-v1", source_name=source.name,
                  valid=False, status="invalid_or_unsupported", normalized=False,
                  ready_for_future_adapter=False, playable_now=False, diagnostics=diagnostics, tracks=[])
    try:
        song, summaries = inspect(source, diagnostics, chart, audio, offset_policy)
        report.update(valid=True, normalized=True, status="imported_with_warnings" if any(d["severity"] == "warning" for d in diagnostics) else "imported_and_normalized",
                      ready_for_future_adapter=not song["package"]["missing_files"] and not any(d["code"] == "MIDI_SYSEX_RETAINED" for d in diagnostics),
                      normalized_data_ready=True, future_adapter_status="inspection only; runtime/audio/lane policies still required",
                      metadata=song["metadata"], source_format=song["source_format"], tracks=summaries,
                      available_instruments=sorted({t["instrument"] for t in song["tracks"] if t["notes"]}),
                      source_track_names=[t["name"] for t in song.get("midi_source_tracks", [])],
                      available_difficulties=[d for d in ("Easy", "Medium", "Hard", "Expert") if any(t["difficulty"] == d and t["notes"] for t in song["tracks"])],
                      resolution=song["resolution"], tempo_map=song["tempo_map"],
                      time_signatures=song["time_signatures"], timing=song["timing"], package=song["package"])
        save_text(destination / "song.json", json.dumps(song, ensure_ascii=False, indent=2) + "\n")
    except InvalidChart as error:
        diagnostic(diagnostics, error.code, str(error), error.line, "error")
    except (OSError, UnicodeError, ValueError, configparser.Error, zipfile.BadZipFile, NotImplementedError, RuntimeError) as error:
        diagnostic(diagnostics, "PACKAGE_READ_ERROR", str(error), severity="error")
    if not report["valid"]:
        (destination / "song.json").unlink(missing_ok=True)
    save_text(destination / "report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    lines = [f"Song package: {source.name}", f"Result: {report['status']}",
             "Playable in current GBA engine: NO; original demo is unchanged.",
             f"Normalized data ready for a FUTURE adapter: {'YES (inspection complete; policies/audio still needed)' if report['ready_for_future_adapter'] else 'NO (see missing files/unsupported features)'}", ""]
    if report["valid"]:
        lines += [f"Title: {report['metadata'].get('Name', '(not supplied)')}",
                  f"Artist: {report['metadata'].get('Artist', '(not supplied)')}",
                  f"Chart format: {report['source_format']}",
                  f"Instruments: {', '.join(report['available_instruments'])}",
                  f"Difficulties: {', '.join(report['available_difficulties'])}",
                  f"Source MIDI track names (including unconverted tracks): {report['source_track_names']}",
                  f"Tempo points: {len(report['tempo_map'])}; meter points: {len(report['time_signatures'])}",
                  f"Offsets: chart {report['timing']['chart_offset_seconds']} seconds; INI delay {report['timing']['song_ini_delay_ms']} ms; effective {report['timing']['effective_offset_seconds']} seconds ({report['timing']['package_offset_policy']})"]
        for point in report["tempo_map"]:
            lines.append(f"  Tempo tick {point['tick']}: " + (f"{point['microseconds_per_quarter']} microseconds/quarter" if 'microseconds_per_quarter' in point else f"{point['milli_bpm']} milli-BPM"))
        for meter in report["time_signatures"]:
            lines.append(f"  Meter tick {meter['tick']}: {meter['numerator']}/{meter['denominator']}")
        for track in report["tracks"]:
            lines.append(f"  {track['instrument']} {track['difficulty']}: {track['note_count']} notes; {track['distinct_playable_lane_count']} used lanes / {track['fret_slots_required']} fret slots; {track['chord_count']} chords; {track['sustain_count']} sustains")
        for stream in report["package"]["audio_streams"]:
            lines.append(f"Audio: {stream['file']} ({stream['format']}, {stream['role']}); detected only, not decoded")
        lines.append("Missing files: " + (", ".join(report["package"]["missing_files"]) or "none detected"))
    lines.extend(f"{d['severity'].upper()} {d['code']}: {d['message']}" for d in diagnostics)
    save_text(destination / "report.txt", "\n".join(lines) + "\n")
    print("\n".join(lines) + f"\n\nReport folder: {destination}\n")
    return report["valid"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("song", type=Path, nargs="?", help="ZIP, folder, .chart or .mid; omit to inspect imports/incoming")
    parser.add_argument("--chart", help="Explicit chart path inside the package, e.g. notes.mid")
    parser.add_argument("--audio", action="append", help="Explicit gameplay audio path inside the package (repeat for stems)")
    parser.add_argument("--offset-policy", choices=("add", "ini", "chart"), help="Resolve conflicting chart Offset and INI delay explicitly")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "imports/output/packages")
    args = parser.parse_args()
    sources = [args.song] if args.song else sorted(p for p in (ROOT / "imports/incoming").iterdir() if p.is_dir() or p.suffix.lower() in {".zip", ".chart", ".mid", ".midi"})
    if not sources:
        parser.error("Put an authorized song ZIP in imports/incoming or supply its path.")
    # Do not overwrite one package's report with another same-stem input.
    stems = [s.stem.casefold() for s in sources]
    if len(stems) != len(set(stems)):
        parser.error("Inputs have identical output names; import each separately with different --output-dir values.")
    valid = True
    for source in sources:
        try:
            valid = import_song(source, args.output_dir, args.chart, args.audio, args.offset_policy) and valid
        except OSError as error:
            print(f"ERROR: cannot write report: {error}", file=sys.stderr)
            valid = False
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
