"""Read-only bounded package inspection; no archive extraction or audio decoding."""
import configparser
from fractions import Fraction
import hashlib
import heapq
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

try:
    from .chart_importer import (InvalidChart, normalize, diagnostic, compatibility,
                                 checked_time, rational, PLANNED_BUTTONS)
    from .midi_importer import normalize_midi
except ImportError:
    from chart_importer import (InvalidChart, normalize, diagnostic, compatibility,
                                checked_time, rational, PLANNED_BUTTONS)
    from midi_importer import normalize_midi

CHARTS = {".chart", ".mid", ".midi"}
AUDIO = {".ogg", ".mp3", ".wav", ".opus"}
STEMS = {"song", "guitar", "rhythm", "bass", "keys", "vocals", "vocals_1", "vocals_2",
         "drums", "drums_1", "drums_2", "drums_3", "drums_4", "crowd"}
MAX_ENTRIES, MAX_TOTAL, MAX_ENTRY = 4096, 2 * 1024**3, 1024**3


def reject(code, message):
    raise InvalidChart(code, message)


class Package:
    def __init__(self, source):
        self.source, self.archive, self.entries = Path(source), None, {}

    def __enter__(self):
        try:
            self._open()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def _open(self):
        if self.source.is_symlink():
            reject("PACKAGE_SYMLINK", "The supplied package must not be a symlink.")
        self.single = self.source.is_file() and self.source.suffix.lower() in CHARTS
        if self.source.is_file() and self.source.suffix.lower() == ".zip":
            self.archive = zipfile.ZipFile(self.source)
            infos = self.archive.infolist()
            if len(infos) > MAX_ENTRIES:
                reject("ZIP_ENTRIES", "ZIP contains more than 4096 entries.")
            total, folded = 0, set()
            for info in infos:
                name = info.filename
                parts = name.rstrip("/").split("/")
                if (not name or "\\" in name or "\x00" in info.orig_filename or
                    any(p in ("", ".", "..") for p in parts) or name.startswith("/") or
                    any(":" in p for p in parts) or any(ord(c) < 32 for c in name)):
                    reject("ZIP_PATH", f"Unsafe ZIP path: {name!r}.")
                folded_name = name.rstrip("/").casefold()
                if folded_name in folded:
                    reject("ZIP_DUPLICATE", "ZIP contains duplicate or case-colliding paths.")
                folded.add(folded_name)
                mode = info.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                    reject("ZIP_SPECIAL_FILE", "ZIP contains a symlink or another special file.")
                if info.flag_bits & 1:
                    reject("ZIP_ENCRYPTED", "Encrypted ZIP entries cannot be inspected.")
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    reject("ZIP_COMPRESSION", "Only stored and deflated ZIP entries are supported.")
                total += info.file_size
                if (info.file_size > MAX_ENTRY or total > MAX_TOTAL or
                    info.file_size > max(info.compress_size, 1) * 1000):
                    reject("ZIP_SIZE", "Suspicious decompression size/ratio: limit 1 GiB per file, 2 GiB total, 1000:1.")
                if not info.is_dir():
                    self.entries[name] = info
        else:
            root = self.source if self.source.is_dir() else self.source.parent
            if not root.is_dir() or (not self.source.is_dir() and not self.single):
                reject("PACKAGE_INPUT", "Supply an extracted folder, ZIP, .chart or .mid file.")
            paths = root.rglob("*") if not self.single else root.iterdir()
            total, folded, count = 0, set(), 0
            for path in paths:
                count += 1
                if count > MAX_ENTRIES:
                    reject("PACKAGE_ENTRIES", "Folder has more than 4096 entries; choose a single song folder.")
                if path.is_symlink():
                    reject("PACKAGE_SYMLINK", "Song folders containing symlinks are not inspected.")
                if path.is_dir():
                    continue
                if not stat.S_ISREG(path.stat().st_mode):
                    reject("PACKAGE_SPECIAL_FILE", "Song folder contains a special file.")
                name = path.relative_to(root).as_posix()
                if name.casefold() in folded:
                    reject("PACKAGE_DUPLICATE", "Case-colliding filenames are ambiguous.")
                folded.add(name.casefold())
                size = path.stat().st_size
                total += size
                if size > MAX_ENTRY or total > MAX_TOTAL:
                    reject("PACKAGE_SIZE", "Folder exceeds 1 GiB per file / 2 GiB total inspection limits.")
                self.entries[name] = path
        # Reject file/directory prefix collisions, including case-insensitive ones.
        names = {name.casefold() for name in self.entries}
        for name in names:
            if any(str(parent) in names for parent in PurePosixPath(name).parents if str(parent) != "."):
                reject("PACKAGE_PATH_COLLISION", "A file is also used as a directory prefix.")

    def read(self, name, limit):
        entry = self.entries[name]
        if self.archive:
            if entry.file_size > limit:
                reject("PACKAGE_READ_LIMIT", f"{name} exceeds its {limit}-byte read limit.")
            with self.archive.open(entry) as stream:
                data = stream.read(limit + 1)  # bounded even with dishonest size metadata
        else:
            with entry.open("rb") as stream:
                data = stream.read(limit + 1)
        if len(data) > limit:
            reject("PACKAGE_READ_LIMIT", f"{name} exceeds its {limit}-byte read limit.")
        return data

    def __exit__(self, *_):
        if self.archive:
            self.archive.close()


def read_ini(data, diagnostics):
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp1252")
        diagnostic(diagnostics, "INI_ENCODING", "song.ini decoded as Windows-1252; retain the original file for provenance.")
    parser = configparser.ConfigParser(interpolation=None, strict=True, inline_comment_prefixes=None)
    parser.read_string(text)
    sections = [s for s in parser.sections() if s.casefold() == "song"]
    if len(sections) != 1 or parser.defaults():
        reject("INI_SECTION", "song.ini requires one [song] section and no DEFAULT overrides.")
    return dict(parser.items(sections[0]))


def decimal(value, label):
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value):
        reject("INI_NUMBER", f"{label} must be a finite decimal number.")
    return Fraction(value)


def shift_song(song, shift):
    """Shift derived times exactly; leave raw MIDI source events untouched."""
    visited = set()
    def apply(item):
        if isinstance(item, (dict, list)):
            if id(item) in visited:
                return
            visited.add(id(item))
        if isinstance(item, list):
            for child in item:
                apply(child)
        elif isinstance(item, dict):
            if "start_us_exact" in item:
                start = Fraction(**item["start_us_exact"]) + shift
                duration = Fraction(**item["duration_us_exact"])
                item.update(start_us_exact=rational(start), start_us=checked_time(start),
                            end_us=checked_time(start + duration))
                item["duration_us"] = checked_time(Fraction(item["end_us"] - item["start_us"]))
            elif "time_us" in item:
                exact = Fraction(**item["time_us_exact"]) if "time_us_exact" in item else Fraction(item["time_us"])
                item["time_us"] = checked_time(exact + shift)
                item["time_us_exact"] = rational(exact + shift)
            for key, value in item.items():
                if key not in ("midi_source_tracks", "unsupported_sections"):
                    apply(value)
    apply(song)


def inspect(source, diagnostics, chart=None, audio=None, offset_policy=None):
    with Package(source) as package:
        candidates = sorted(n for n in package.entries if PurePosixPath(n).suffix.lower() in CHARTS)
        if package.single:
            chart = package.source.name
        if chart is None:
            if len(candidates) != 1:
                reject("CHART_SELECTION", f"Select one chart with --chart RELATIVE_PATH. Candidates: {candidates or '(none; chart is missing)' }.")
            chart = candidates[0]
        if chart not in candidates:
            reject("CHART_SELECTION", f"Selected chart is not a recognized package file. Candidates: {candidates}.")
        parent = PurePosixPath(chart).parent
        siblings = sorted(n for n in package.entries if PurePosixPath(n).parent == parent)
        ini_names = [n for n in siblings if PurePosixPath(n).name.casefold() == "song.ini"]
        ini = read_ini(package.read(ini_names[0], 1024**2), diagnostics) if ini_names else {}
        if not ini:
            diagnostic(diagnostics, "MISSING_INI", "song.ini is missing/empty; title, artist and timing overrides may be unavailable.")
        data = package.read(chart, 32 * 1024**2)
        fmt = "midi" if PurePosixPath(chart).suffix.lower() in (".mid", ".midi") else "chart"
        song = normalize_midi(data, chart, diagnostics) if fmt == "midi" else normalize(data.decode("utf-8-sig"), chart, diagnostics)
        if fmt == "chart":
            diagnostics[:] = [d for d in diagnostics if d["code"] != "AUDIO_UNVERIFIED"]
        song.update(schema_revision=2, source_format=fmt, source_sha256=hashlib.sha256(data).hexdigest())
        original_metadata = dict(song["metadata"])
        for key, target in (("name", "Name"), ("artist", "Artist"), ("charter", "Charter"),
                            ("album", "Album"), ("year", "Year")):
            if key in ini:
                song["metadata"][target] = ini[key]
        if "charter" not in ini and "frets" in ini:
            song["metadata"]["Charter"] = ini["frets"]
        delay = decimal(ini.get("delay", "0"), "song.ini delay (milliseconds)") * 1000
        chart_offset = Fraction(song["timing"]["offset_seconds"]) * 1_000_000
        checked_time(delay)
        if delay and chart_offset and offset_policy is None:
            reject("OFFSET_SELECTION", "Both chart Offset and song.ini delay are nonzero. Choose --offset-policy add, ini, or chart after checking the intended timing.")
        policy = offset_policy or "add"
        effective = delay + chart_offset if policy == "add" else delay if policy == "ini" else chart_offset
        shift_song(song, effective - chart_offset)
        song["timing"].update(chart_offset_seconds=str(chart_offset / 1_000_000),
                              song_ini_delay_ms=str(delay / 1000), effective_offset_seconds=str(effective / 1_000_000),
                              package_offset_policy=policy, offset_policy="explicit package policy: " + policy)
        streams = []
        for name in siblings:
            path = PurePosixPath(name)
            if path.suffix.lower() in AUDIO:
                role = "preview" if path.stem.casefold() == "preview" else path.stem.casefold() if path.stem.casefold() in STEMS else "unassigned"
                streams.append(dict(file=name, format=path.suffix.lower()[1:], role=role, decoded=False))
        selected = set(audio or [])
        stream_names = {s["file"] for s in streams}
        if selected - stream_names:
            reject("AUDIO_SELECTION", f"Selected audio is not beside the chosen chart: {sorted(selected - stream_names)}.")
        roles = [s["role"] for s in streams if s["role"] != "preview"]
        ambiguous = "unassigned" in roles or len(roles) != len(set(roles))
        if ambiguous and not selected:
            reject("AUDIO_SELECTION", f"Ambiguous audio layout. Select gameplay files with repeated --audio RELATIVE_PATH. Detected: {sorted(stream_names)}.")
        for stream in streams:
            stream["selected_for_future_adapter"] = stream["file"] in selected if selected else stream["role"] != "preview"
        missing = []
        if not ini_names:
            missing.append("song.ini (metadata recommended; required for normal MIDI packages)")
        if not any(s["selected_for_future_adapter"] and s["role"] != "preview" for s in streams):
            missing.append("gameplay audio")
            diagnostic(diagnostics, "MISSING_AUDIO", "No selected gameplay audio found. Preview audio is never a gameplay substitute.")
        # Preserve all INI values, including difficulty, audio, HOPO and sustain declarations.
        declarations = {k: v for k, v in ini.items() if "audio" in k or k.endswith("stream") or k in ("music_stream", "guitar_stream", "rhythm_stream")}
        for key, value in declarations.items():
            declared = str(parent / value.strip('"'))
            if declared not in stream_names:
                diagnostic(diagnostics, "AUDIO_DECLARATION", f"INI {key}={value!r} does not match a detected audio file; declaration retained, not guessed.")
        if any(k in ini for k in ("hopo_frequency", "hopofreq", "eighthnote_hopo", "sustain_cutoff_threshold", "multiplier_note", "star_power_note")):
            diagnostic(diagnostics, "INI_GAMEPLAY_POLICY", "INI HOPO/sustain/star-power overrides retained but not applied. Native note lengths/markers are preserved.")
        diagnostic(diagnostics, "AUDIO_DISCOVERY_ONLY", "Audio names/extensions detected only; codec validity, duration, synchronization and rights are unverified.")
        song["package"] = dict(chart_file=chart, chart_candidates=candidates, song_ini=ini,
                               chart_metadata=original_metadata, audio_streams=streams,
                               inventory=sorted(package.entries), missing_files=missing,
                               artwork=[n for n in siblings if PurePosixPath(n).suffix.lower() in (".png", ".jpg", ".jpeg")])
        summaries = compatibility(song, diagnostics)
        for track, summary in zip(song["tracks"], summaries):
            summary.update(instrument=track["instrument"], distinct_playable_lane_count=len(summary["logical_lanes"]))
            # Sweep sustained occupancy in tick space; each lane has a min-heap
            # of end ticks. Adjacent releases are not simultaneous holds.
            buttons = PLANNED_BUTTONS.get(track["difficulty"], [])
            occupied = {button: [] for button in ("Left", "Up", "Right")}
            overlaps = []
            for note in sorted(track["notes"], key=lambda n: (n["tick"], n["source_order"])):
                lane = note["lane"]
                if lane is None or lane >= len(buttons) or buttons[lane] not in occupied:
                    continue
                tick, direction = note["tick"], buttons[lane]
                for held, ends in occupied.items():
                    while ends and ends[0] <= tick:
                        heapq.heappop(ends)
                    if ends and held != direction:
                        overlaps.append(dict(tick=tick, directions=sorted([held, direction]),
                                             kind="opposing_directions" if {held, direction} == {"Left", "Right"} else "diagonal_requires_playtest"))
                if note["duration_ticks"]:
                    heapq.heappush(occupied[direction], tick + note["duration_ticks"])
            summary["sustain_dpad_conflicts"] = overlaps
            summary["dpad_validation_scope"] = "same-tick onsets and overlapping native sustains; human ergonomics unverified"
            if overlaps:
                diagnostic(diagnostics, "DPAD_SUSTAIN_OVERLAP", f"{track['section']}: {len(overlaps)} overlapping sustained D-pad combinations; no notes changed.")
            if track["instrument"] != "five_fret_lead_guitar":
                summary["current_four_lane_note_shapes_compatible"] = False
                diagnostic(diagnostics, "INSTRUMENT_NOT_PLAYABLE", f"{track['instrument']} is normalized for inspection; the engine only has its original lead-guitar demo.")
        return song, summaries
