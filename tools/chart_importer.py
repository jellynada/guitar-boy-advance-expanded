"""Strict 5-fret .chart import; exact song timing, no rendering/audio dependencies."""
from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
import re

MAX_TICK = (1 << 64) - 1
MAX_TIME = (1 << 63) - 1
MIN_TIME = -(1 << 63)
TRACKS = {f"{d}Single": d for d in ("Easy", "Medium", "Hard", "Expert")}
PLANNED_BUTTONS = {
    "Easy": ["Left", "A", "B"],
    "Medium": ["Left", "Right", "A", "B"],
    "Hard": ["Left", "Up", "Right", "A", "B"],
}


class InvalidChart(ValueError):
    def __init__(self, code, message, line=None):
        super().__init__(message)
        self.code, self.line = code, line


@dataclass(frozen=True)
class Row:
    line: int
    text: str


def diagnostic(items, code, message, line=None, severity="warning"):
    items.append(dict(severity=severity, code=code, message=message, line=line))


def strip_comment(line):
    quoted = escaped = False
    for i, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\" and quoted:
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and line[i:i + 2] == "//":
            return line[:i].strip()
    return line.strip()


def parse_sections(text):
    sections, active, awaiting = {}, None, False
    for number, raw in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        line = strip_comment(raw)
        if not line:
            continue
        match = re.fullmatch(r"\[([A-Za-z0-9_]+)\]\s*(\{)?", line)
        if match:
            if active is not None:
                raise InvalidChart("UNCLOSED_SECTION", "Close the previous section before starting another.", number)
            active = match[1]
            if active in sections:
                raise InvalidChart("DUPLICATE_SECTION", f"Section [{active}] occurs twice.", number)
            sections[active] = []
            awaiting = not bool(match[2])
        elif active is None:
            raise InvalidChart("OUTSIDE_SECTION", "Expected [SectionName].", number)
        elif awaiting:
            if line != "{":
                raise InvalidChart("MISSING_BRACE", "Expected an opening { after the section name.", number)
            awaiting = False
        elif line == "}":
            active = None
        elif line == "{":
            raise InvalidChart("NESTED_BRACE", "Unexpected opening brace.", number)
        else:
            sections[active].append(Row(number, line))
    if active is not None:
        raise InvalidChart("UNCLOSED_SECTION", f"Section [{active}] is not closed.")
    return sections


def unsigned(value, name, line, maximum=MAX_TICK, positive=False):
    if not re.fullmatch(r"\d+", value):
        raise InvalidChart("INVALID_NUMBER", f"{name} must be an unsigned integer.", line)
    try:
        number = int(value)
    except ValueError:
        raise InvalidChart("NUMBER_RANGE", f"{name} has too many digits to parse.", line) from None
    if number > maximum or (positive and number == 0):
        raise InvalidChart("NUMBER_RANGE", f"{name} is outside the supported range (max {maximum}).", line)
    return number


def metadata_value(value, line):
    if value.startswith('"'):
        if not re.fullmatch(r'"(?:[^"\\]|\\.)*"', value):
            raise InvalidChart("INVALID_STRING", "Unclosed or malformed metadata string.", line)
        return re.sub(r'\\(["\\])', r'\1', value[1:-1])
    if not value or '"' in value:
        raise InvalidChart("INVALID_VALUE", "Malformed metadata value.", line)
    return value


def event_rows(rows):
    previous = -1
    seen = set()
    for row in rows:
        match = re.fullmatch(r"(\d+)\s*=\s*([A-Za-z]+)\s+(.+)", row.text)
        if not match:
            raise InvalidChart("MALFORMED_EVENT", "Expected tick = event_type values.", row.line)
        tick = unsigned(match[1], "Event tick", row.line)
        if tick < previous:
            raise InvalidChart("UNSORTED_EVENTS", "Events must be in nondecreasing tick order; nothing is silently reordered.", row.line)
        previous = tick
        payload = match[3].strip()
        key = (tick, match[2], payload)
        if key in seen:
            raise InvalidChart("DUPLICATE_EVENT", "Duplicate event at the same tick; resolve it rather than dropping it.", row.line)
        seen.add(key)
        yield row, tick, match[2], payload


def rounded(value):
    """Nearest integer; exact halves go away from zero, including negative offsets."""
    sign = -1 if value < 0 else 1
    numerator = abs(value.numerator)
    return sign * ((2 * numerator + value.denominator) // (2 * value.denominator))


def checked_time(value, line=None):
    # Check the exact value as well as the rounded value: never hide overflow.
    if not MIN_TIME <= value <= MAX_TIME:
        raise InvalidChart("TIME_OVERFLOW", "Timestamp cannot fit signed 64-bit microseconds.", line)
    return rounded(value)


def rational(value):
    return dict(numerator=value.numerator, denominator=value.denominator)


class TempoMap:
    def __init__(self, resolution, tempos, offset):
        self.resolution, self.offset = resolution, offset
        self.tempos = tempos
        self.ticks = [point[0] for point in tempos]
        self.starts = [Fraction(0)]
        for (tick, _), (previous, bpm) in zip(tempos[1:], tempos):
            self.starts.append(self.starts[-1] + Fraction((tick - previous) * 60_000_000_000, resolution * bpm))

    def time(self, tick):
        i = bisect_right(self.ticks, tick) - 1
        start, bpm = self.tempos[i]
        return self.offset + self.starts[i] + Fraction((tick - start) * 60_000_000_000, self.resolution * bpm)

    def span(self, tick, duration, line):
        if tick + duration > MAX_TICK:
            raise InvalidChart("TICK_OVERFLOW", "Sustain end tick exceeds unsigned 64-bit range.", line)
        start, end = self.time(tick), self.time(tick + duration)
        start_us, end_us = checked_time(start, line), checked_time(end, line)
        if end - start > MAX_TIME or end_us - start_us > MAX_TIME:
            raise InvalidChart("DURATION_OVERFLOW", "Sustain duration exceeds signed 64-bit microseconds.", line)
        return dict(tick=tick, duration_ticks=duration, start_us=start_us,
                    end_us=end_us, duration_us=end_us - start_us,
                    start_us_exact=rational(start), duration_us_exact=rational(end - start))


def normalize(text, source_name="chart.chart", diagnostics=None):
    warnings = diagnostics if diagnostics is not None else []
    sections = parse_sections(text)
    for required in ("Song", "SyncTrack"):
        if required not in sections:
            raise InvalidChart("MISSING_SECTION", f"Required [{required}] section is missing.")
    metadata, metadata_lines = {}, {}
    for row in sections["Song"]:
        match = re.fullmatch(r"([A-Za-z0-9_]+)\s*=\s*(.+)", row.text)
        if not match:
            raise InvalidChart("MALFORMED_METADATA", "Expected metadata_name = value.", row.line)
        key = match[1]
        if key in metadata:
            raise InvalidChart("DUPLICATE_METADATA", f"Metadata {key} occurs twice.", row.line)
        metadata[key] = metadata_value(match[2], row.line)
        metadata_lines[key] = row.line
    if "Resolution" not in metadata:
        raise InvalidChart("MISSING_RESOLUTION", "[Song] needs a positive Resolution.")
    resolution = unsigned(metadata["Resolution"], "Resolution", metadata_lines["Resolution"], (1 << 32) - 1, True)
    offset_text = metadata.get("Offset", "0")
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", offset_text):
        raise InvalidChart("INVALID_OFFSET", "Offset must be a finite decimal number of seconds.", metadata_lines.get("Offset"))
    try:
        offset = Fraction(offset_text) * 1_000_000
    except ValueError:
        raise InvalidChart("INVALID_OFFSET", "Offset has too many digits to parse.", metadata_lines.get("Offset")) from None
    checked_time(offset, metadata_lines.get("Offset"))

    tempos, signatures, anchors = [], [], []
    seen_sync = set()
    for row, tick, kind, rest in event_rows(sections["SyncTrack"]):
        if (tick, kind) in seen_sync:
            raise InvalidChart("DUPLICATE_SYNC", f"Duplicate {kind} event at tick {tick}; resolve the ambiguity.", row.line)
        seen_sync.add((tick, kind))
        parts = rest.split()
        if kind == "B" and len(parts) == 1:
            tempos.append((tick, unsigned(parts[0], "BPM in thousandths", row.line, (1 << 32) - 1, True)))
        elif kind == "TS" and len(parts) in (1, 2):
            numerator = unsigned(parts[0], "Time-signature numerator", row.line, (1 << 32) - 1, True)
            exponent = unsigned(parts[1] if len(parts) == 2 else "2", "Time-signature denominator exponent", row.line, 31)
            signatures.append(dict(tick=tick, numerator=numerator, denominator=1 << exponent))
        elif kind == "A" and len(parts) == 1:
            anchors.append(dict(tick=tick, audio_time_us=unsigned(parts[0], "Anchor time", row.line, MAX_TIME), source_line=row.line))
        else:
            raise InvalidChart("UNSUPPORTED_SYNC", f"Malformed or unsupported SyncTrack event: {kind} {rest}.", row.line)
    if not tempos or tempos[0][0] != 0:
        raise InvalidChart("MISSING_INITIAL_TEMPO", "Provide B at tick 0; this importer does not invent a default BPM.")
    clock = TempoMap(resolution, tempos, offset)
    tempo_points = [dict(tick=tick, milli_bpm=bpm, time_us=checked_time(clock.time(tick)),
                         time_us_exact=rational(clock.time(tick))) for tick, bpm in tempos]
    if not signatures or signatures[0]["tick"] != 0:
        diagnostic(warnings, "NO_INITIAL_METER", "No explicit TS at tick 0. Meter remains unspecified; tempo-based time conversion does not need a meter.")
    for anchor in anchors:
        diagnostic(warnings, "EDITOR_ANCHOR", "Editor tempo anchor retained, not applied as a second timing override.", anchor["source_line"], "info")
        if abs(clock.time(anchor["tick"]) - anchor["audio_time_us"]) > 1:
            diagnostic(warnings, "ANCHOR_CONFLICT", "Anchor differs from the tempo-map/audio-origin time; verify the chart's tempo/offset in its editor.", anchor["source_line"])

    tracks = []
    for name, rows in sections.items():
        if name not in TRACKS:
            continue
        notes, modifiers, special = [], [], []
        seen_notes = set()
        for order, (row, tick, kind, rest) in enumerate(event_rows(rows)):
            parts = rest.split()
            if kind == "N" and len(parts) == 2:
                lane = unsigned(parts[0], "Note identifier", row.line, 7)
                duration = unsigned(parts[1], "Sustain ticks", row.line)
                key = (tick, lane)
                if key in seen_notes:
                    raise InvalidChart("DUPLICATE_NOTE", f"Duplicate note/modifier {lane} at tick {tick}.", row.line)
                seen_notes.add(key)
                span = clock.span(tick, duration, row.line)
                record = dict(**span, source_line=row.line, source_order=order, source_lane=lane)
                if lane in (5, 6):
                    record["kind"] = "hopo_flip" if lane == 5 else "tap"
                    modifiers.append(record)
                else:
                    record.update(kind="open" if lane == 7 else "fretted", lane=None if lane == 7 else lane)
                    notes.append(record)
            elif kind == "S" and len(parts) == 2:
                phrase = unsigned(parts[0], "Phrase identifier", row.line, (1 << 32) - 1)
                span = clock.span(tick, unsigned(parts[1], "Phrase duration", row.line), row.line)
                special.append(dict(**span, kind="phrase", phrase_id=phrase, source_line=row.line, source_order=order))
            elif kind == "E":
                special.append(dict(tick=tick, time_us=checked_time(clock.time(tick), row.line),
                                    kind="text", text=metadata_value(rest, row.line), source_line=row.line, source_order=order))
            else:
                raise InvalidChart("UNSUPPORTED_NOTE_EVENT", f"Malformed or unsupported track event: {kind} {rest}.", row.line)
        if modifiers:
            diagnostic(warnings, "MODIFIERS_PREPARED", f"[{name}] HOPO/tap markers are preserved; their gameplay semantics are not implemented.")
        note_ticks = {note["tick"] for note in notes}
        for modifier in modifiers:
            if modifier["tick"] not in note_ticks and modifier["duration_ticks"] == 0:
                raise InvalidChart("ORPHAN_MODIFIER", "A point HOPO/tap modifier must accompany a note at the same tick.", modifier["source_line"])
            if modifier["duration_ticks"]:
                diagnostic(warnings, "RANGE_MODIFIER", "Nonzero-duration modifier preserved; range semantics are not interpreted.", modifier["source_line"])
        if special:
            diagnostic(warnings, "SPECIAL_EVENTS_PREPARED", f"[{name}] phrase/text events retained in JSON only; no star power, solo or other gameplay added.")
        if not notes:
            diagnostic(warnings, "EMPTY_TRACK", f"[{name}] is present but contains no playable note records.")
        tracks.append(dict(section=name, difficulty=TRACKS[name], instrument="five_fret_lead_guitar",
                           notes=notes, modifiers=modifiers, special_events=special))
    if not tracks or not any(track["notes"] for track in tracks):
        raise InvalidChart("NO_SUPPORTED_NOTES", "No nonempty EasySingle/MediumSingle/HardSingle/ExpertSingle guitar tracks found.")

    global_events = []
    for row, tick, kind, rest in event_rows(sections.get("Events", [])):
        # Retain all global payloads, including practice/lyric/animation events;
        # never mistake them for playable guitar notes.
        global_events.append(dict(tick=tick, time_us=checked_time(clock.time(tick), row.line),
                                  type=kind, payload=rest, source_line=row.line))
    if global_events:
        diagnostic(warnings, "GLOBAL_EVENTS_PREPARED", "Global events preserved in JSON; not implemented in runtime or generated note arrays.")
    unsupported = {name: [dict(line=row.line, text=row.text) for row in rows]
                   for name, rows in sections.items() if name not in TRACKS and name not in ("Song", "SyncTrack", "Events")}
    for name in unsupported:
        diagnostic(warnings, "UNSUPPORTED_TRACK", f"[{name}] is preserved as raw rows in JSON, not converted into guitar notes.")
    diagnostic(warnings, "NO_RUNTIME_BINDING", "Prepared absolute-time data is not connected to the live legacy-clock demo. Import does not replace its chart/audio.")
    diagnostic(warnings, "AUDIO_UNVERIFIED", "No audio was read, downloaded, paired or licensed. Confirm the exact recording and any song.ini timing overrides separately.")
    return dict(schema_version="gba-song-data-v1", source_name=source_name,
                timing=dict(unit="microseconds", offset_seconds=str(Fraction(offset_text)),
                            offset_explicit="Offset" in metadata, offset_policy="audio_origin_time = chart_tempo_time + chart_Offset_seconds",
                            rounding="nearest_integer_half_away_from_zero; duration = rounded_end - rounded_start"),
                metadata=metadata, resolution=resolution, tempo_map=tempo_points,
                time_signatures=signatures, anchors=anchors, tracks=tracks,
                global_events=global_events, unsupported_sections=unsupported)


def compatibility(song, diagnostics):
    summaries = []
    for track in song["tracks"]:
        notes, difficulty = track["notes"], track["difficulty"]
        lanes = sorted({note["lane"] for note in notes if note["lane"] is not None})
        slots = max(lanes, default=-1) + 1
        buttons = PLANNED_BUTTONS.get(difficulty)
        if buttons and slots > len(buttons):
            diagnostic(diagnostics, "PLANNED_LAYOUT_TOO_SMALL", f"[{track['section']}] requires {slots} logical fret slots; planned {difficulty} has {len(buttons)}. Lanes are not collapsed.")
        if difficulty == "Expert":
            diagnostic(diagnostics, "EXPERT_NOT_REMAPPED", "Expert stays Expert; it is not automatically relabeled Hard or Medium.")
        chords = defaultdict(list)
        for note in notes:
            chords[note["tick"]].append(note)
        chord_count = sum(len(group) > 1 for group in chords.values())
        mapping = buttons if buttons else (PLANNED_BUTTONS["Medium"] if slots <= 4 else [])
        dpad_conflicts = []
        for tick, group in chords.items():
            directions = {mapping[note["lane"]] for note in group
                          if note["lane"] is not None and note["lane"] < len(mapping)
                          and mapping[note["lane"]] in ("Left", "Up", "Right")}
            if {"Left", "Right"} <= directions:
                dpad_conflicts.append(dict(tick=tick, kind="opposing_directions"))
            elif len(directions) > 1:
                dpad_conflicts.append(dict(tick=tick, kind="diagonal_requires_playtest"))
            if any(n["kind"] == "open" for n in group) and len(group) > 1:
                diagnostic(diagnostics, "OPEN_CHORD", f"[{track['section']}] open-note chord at tick {tick} retained; no open-note gameplay exists.")
        if dpad_conflicts:
            diagnostic(diagnostics, "DPAD_CHORDS", f"[{track['section']}] has {len(dpad_conflicts)} opposing/diagonal D-pad chord combinations; see track report.")
        sustains = sum(note["duration_ticks"] > 0 for note in notes)
        opens = sum(note["kind"] == "open" for note in notes)
        if sustains:
            diagnostic(diagnostics, "SUSTAINS_PREPARED", f"[{track['section']}] retains {sustains} sustains, including tempo-aware end times; gameplay not implemented.")
        if opens or slots > 4:
            diagnostic(diagnostics, "RENDERER_UNSUPPORTED", f"[{track['section']}] open/five-lane data is prepared but cannot use the current four-lane renderer.")
        if any(note["start_us"] < 0 for note in notes):
            diagnostic(diagnostics, "NEGATIVE_TIME", f"[{track['section']}] contains pre-audio-origin notes; a future playback adapter needs pre-roll policy.")
        summaries.append(dict(section=track["section"], difficulty=difficulty, note_count=len(notes),
                              logical_lanes=lanes, fret_slots_required=slots, chord_count=chord_count,
                              sustain_count=sustains, open_note_count=opens, modifier_count=len(track["modifiers"]),
                              special_event_count=len(track["special_events"]), prepared=bool(notes),
                              dpad_validation_scope="same-tick onsets; sustain overlap/ergonomics require future validation",
                              planned_button_layout=buttons, dpad_conflicts=dpad_conflicts,
                              current_four_lane_note_shapes_compatible=bool(notes) and slots <= 4 and not opens and not sustains and not track["modifiers"],
                              playable_now=False, reason="No runtime/audio adapter is enabled; imported data uses absolute microseconds."))
    return summaries


def cpp_assets(song, digest):
    lines = ["// Generated prepared data. NOT the live demo Note ABI; no runtime binding.",
             "#pragma once", "#include <array>", "#include <cstdint>",
             f"namespace imported_song_{digest[:12]} {{",
             "struct Note { int64_t start_us; int64_t duration_us; uint8_t lane; uint8_t kind; };",
             "// kind: 0 = fretted (lane 0..4), 1 = open (lane 255).",
             "struct Modifier { int64_t start_us; int64_t duration_us; uint8_t kind; };",
             "// modifier kind: 5 = strum/HOPO flip, 6 = tap; not applied to gameplay.",
             "struct Tempo { uint64_t tick; uint32_t milli_bpm; int64_t time_us; };",
             "struct Meter { uint64_t tick; uint32_t numerator; uint32_t denominator; };"]

    def signed(value):
        return "(-9223372036854775807LL - 1)" if value == MIN_TIME else f"{value}LL"

    def array(kind, name, rows):
        lines.append(f"inline constexpr std::array<{kind}, {len(rows)}> {name}{{{{")
        lines.extend("    {" + ", ".join(row) + "}," for row in rows)
        lines.append("}};")

    array("Tempo", "tempos", [[f"{p['tick']}ULL", f"{p['milli_bpm']}U", signed(p["time_us"])] for p in song["tempo_map"]])
    array("Meter", "meters", [[f"{p['tick']}ULL", f"{p['numerator']}U", f"{p['denominator']}U"] for p in song["time_signatures"]])
    for track in song["tracks"]:
        name = track["difficulty"].lower() + "_single"
        array("Note", name + "_notes", [[signed(n["start_us"]), signed(n["duration_us"]),
              str(255 if n["lane"] is None else n["lane"]), str(int(n["kind"] == "open"))] for n in track["notes"]])
        array("Modifier", name + "_modifiers", [[signed(n["start_us"]), signed(n["duration_us"]), str(n["source_lane"])] for n in track["modifiers"]])
    lines.extend(["} // namespace", ""])
    return "\n".join(lines)
