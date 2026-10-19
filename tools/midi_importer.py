"""Bounded Standard MIDI File reader and Clone Hero five-fret normalization.

No MIDI playback, external dependencies, repair heuristics or guessed tempos.
See docs/SONG_PACKAGE_IMPORT.md for the supported semantic subset.
"""
from collections import defaultdict
from fractions import Fraction
import struct

try:
    from .chart_importer import InvalidChart, TempoMap, checked_time, diagnostic, rational
except ImportError:
    from chart_importer import InvalidChart, TempoMap, checked_time, diagnostic, rational

MAX_BYTES = 32 * 1024 * 1024
MAX_EVENTS = 250_000
DIFFICULTIES = ("Easy", "Medium", "Hard", "Expert")
INSTRUMENTS = {"PART GUITAR": "five_fret_lead_guitar", "T1 GEMS": "five_fret_lead_guitar",
               "PART BASS": "five_fret_bass", "PART RHYTHM": "five_fret_rhythm",
               "PART GUITAR COOP": "five_fret_coop", "PART KEYS": "five_lane_keys"}
MARKERS = {104: "tap", 103: "solo_or_legacy_star_power", 105: "player_1_phrase",
           106: "player_2_phrase", 116: "star_power", 126: "tremolo", 127: "trill",
           **{n: "big_rock_ending" for n in range(120, 125)}}


def fail(code, message):
    raise InvalidChart(code, message)


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, count):
        if count > len(self.data) - self.pos:
            fail("MIDI_TRUNCATED", f"Unexpected end of MIDI data at byte {self.pos}.")
        result = self.data[self.pos:self.pos + count]
        self.pos += count
        return result

    def byte(self):
        return self.take(1)[0]

    def vlq(self):
        value = 0
        for _ in range(4):
            part = self.byte()
            value = (value << 7) | (part & 127)
            if not part & 128:
                return value
        fail("MIDI_VLQ", "MIDI variable-length number exceeds four bytes.")


def parse_midi(data):
    if len(data) > MAX_BYTES:
        fail("MIDI_SIZE", "MIDI exceeds the 32 MiB inspection limit.")
    reader = Reader(data)
    if reader.take(4) != b"MThd":
        fail("MIDI_HEADER", "Expected a Standard MIDI File MThd header.")
    length = int.from_bytes(reader.take(4), "big")
    header = reader.take(length)
    if length < 6:
        fail("MIDI_HEADER", "MIDI header is shorter than six bytes.")
    fmt, count, resolution = struct.unpack(">HHH", header[:6])
    if fmt not in (0, 1) or not count or (fmt == 0 and count != 1):
        fail("MIDI_FORMAT", "Only Type 0 (one track) and Type 1 simultaneous-track MIDI are supported.")
    if not resolution or resolution & 0x8000:
        fail("MIDI_RESOLUTION", "Use positive ticks-per-quarter-note MIDI, not SMPTE timing.")
    tracks, total = [], 0
    for index in range(count):
        if reader.take(4) != b"MTrk":
            fail("MIDI_CHUNK", "Expected an MTrk chunk matching the declared track count.")
        track = Reader(reader.take(int.from_bytes(reader.take(4), "big")))
        events, tick, running, ended = [], 0, None, False
        while track.pos < len(track.data):
            tick += track.vlq()
            status = track.byte()
            if status < 128:
                if running is None:
                    fail("MIDI_RUNNING_STATUS", "Running status has no preceding channel event (or follows a meta/SysEx reset).")
                track.pos -= 1
                status = running
            event = dict(tick=tick, order=len(events), track_index=index, status=status)
            if 0x80 <= status <= 0xEF:
                running = status
                size = 1 if status >> 4 in (12, 13) else 2
                payload = track.take(size)
                if any(value >= 128 for value in payload):
                    fail("MIDI_CHANNEL_DATA", "A channel event contains an unexpected status byte.")
                event.update(type="channel", channel=status & 15, data=list(payload))
            elif status in (0xF0, 0xF7):
                running = None
                event.update(type="sysex", data_hex=track.take(track.vlq()).hex())
            elif status == 0xFF:
                running = None
                meta = track.byte()
                if meta >= 128:
                    fail("MIDI_META", "Invalid MIDI meta-event type.")
                payload = track.take(track.vlq())
                event.update(type="meta", meta_type=meta, data_hex=payload.hex())
                if 1 <= meta <= 15:
                    try:
                        event["text"] = payload.decode("utf-8")
                    except UnicodeDecodeError:
                        event["text"] = payload.decode("latin-1")
                        event["text_encoding"] = "latin-1 fallback; original bytes retained"
                if meta == 0x2F:
                    if payload or track.pos != len(track.data):
                        fail("MIDI_END_TRACK", "End-of-track must have zero length and be the last event.")
                    ended = True
            else:
                fail("MIDI_STATUS", f"Unsupported MIDI system status 0x{status:02X}.")
            events.append(event)
            total += 1
            if total > MAX_EVENTS:
                fail("MIDI_EVENTS", "MIDI exceeds the 250,000-event inspection limit.")
        if not ended:
            fail("MIDI_END_TRACK", "A track has no required end-of-track event.")
        names = [e["text"] for e in events if e.get("meta_type") == 3]
        if len(set(names)) > 1:
            fail("MIDI_TRACK_NAME", "A MIDI track changes its name; instrument identity is ambiguous.")
        tracks.append(dict(name=names[0] if names else "", events=events))
    if reader.pos != len(data):
        fail("MIDI_TRAILING_DATA", "Unexpected bytes/chunks after the declared MIDI tracks.")
    return fmt, resolution, tracks


def normalize_midi(data, source_name="notes.mid", diagnostics=None):
    warnings = diagnostics if diagnostics is not None else []
    fmt, resolution, raw_tracks = parse_midi(data)
    tempos, meters = {}, {}
    for track in raw_tracks:
        for event in track["events"]:
            kind, tick = event.get("meta_type"), event["tick"]
            if kind not in (0x51, 0x58):
                if kind == 0x54:
                    fail("MIDI_SMPTE_OFFSET", "SMPTE offsets are not interpreted; remove/resolve this timing override explicitly.")
                continue
            raw = bytes.fromhex(event["data_hex"])
            if kind == 0x51:
                if len(raw) != 3 or int.from_bytes(raw, "big") == 0:
                    fail("MIDI_TEMPO", "Tempo must contain three bytes and a positive microseconds-per-quarter value.")
                value, target = int.from_bytes(raw, "big"), tempos
            else:
                if len(raw) != 4 or raw[0] == 0 or raw[1] > 31:
                    fail("MIDI_METER", "Time signature must have four bytes, positive numerator and denominator exponent <=31.")
                value, target = tuple(raw), meters
            if tick in target and target[tick] != value:
                fail("MIDI_SYNC_CONFLICT", f"Conflicting MIDI timing events at tick {tick}.")
            target[tick] = value
    if 0 not in tempos:
        fail("MISSING_INITIAL_TEMPO", "Provide a MIDI tempo event at tick 0; no default BPM is guessed.")
    # TempoMap already integrates rational milli-BPM exactly. MIDI values need not
    # have an integral milli-BPM; never round them before computing timestamps.
    clock = TempoMap(resolution, [(tick, Fraction(60_000_000_000, us)) for tick, us in sorted(tempos.items())], Fraction(0))
    points = [dict(tick=tick, milli_bpm=None, microseconds_per_quarter=us,
                   milli_bpm_exact=rational(Fraction(60_000_000_000, us)),
                   time_us=checked_time(clock.time(tick)), time_us_exact=rational(clock.time(tick)))
              for tick, us in sorted(tempos.items())]
    signatures = [dict(tick=t, numerator=v[0], denominator=1 << v[1],
                       midi_clocks_per_click=v[2], notated_32nds_per_quarter=v[3]) for t, v in sorted(meters.items())]
    if 0 not in meters:
        diagnostic(warnings, "NO_INITIAL_METER", "No explicit MIDI meter at tick zero; meter remains unspecified.")
    tracks, unsupported, global_events, identities = [], {}, [], set()
    for index, raw_track in enumerate(raw_tracks):
        name, events = raw_track["name"], raw_track["events"]
        instrument = INSTRUMENTS.get(name)
        if instrument and instrument in identities:
            fail("MIDI_DUPLICATE_INSTRUMENT", f"Multiple tracks describe {instrument}; explicit chart editing is required.")
        if instrument:
            identities.add(instrument)
        enhanced = any(e.get("text", "").strip("[]") == "ENHANCED_OPENS" and e["tick"] == 0 for e in events)
        active, pairs = {}, []
        for event in events:
            if event["type"] != "channel" or event["status"] >> 4 not in (8, 9):
                if event["type"] == "sysex":
                    payload = bytes.fromhex(event["data_hex"])
                    marker = "unrecognized_sysex"
                    if payload.startswith(b"PS\x00") and len(payload) in (7, 8):
                        marker = {1: "open_phrase", 4: "tap_phrase"}.get(payload[5], marker)
                    event["recognized_marker"] = marker
                    diagnostic(warnings, "MIDI_SYSEX_RETAINED", f"{name or 'unnamed track'}: {marker} retained, not applied; lane interpretation may be incomplete.")
                continue
            pitch, velocity = event["data"]
            key = event["channel"], pitch
            if event["status"] >> 4 == 9 and velocity:
                if key in active:
                    fail("MIDI_OVERLAPPING_NOTE", f"Track {index}: overlapping note-ons on channel {key[0]}, pitch {pitch}; pairing is ambiguous.")
                active[key] = event
            else:
                if key not in active:
                    fail("MIDI_UNPAIRED_OFF", f"Track {index}: note-off without note-on for pitch {pitch}.")
                start = active.pop(key)
                pairs.append((start, event["tick"] - start["tick"]))
        if active:
            fail("MIDI_UNCLOSED_NOTE", f"Track {index}: note-on has no matching note-off.")
        if not instrument:
            if name == "EVENTS":
                global_events.extend(dict(**e, time_us=checked_time(clock.time(e["tick"])), time_us_exact=rational(clock.time(e["tick"]))) for e in events if "text" in e)
            unsupported[f"{index}:{name}"] = events
            if pairs or any(e["type"] == "sysex" for e in events):
                diagnostic(warnings, "UNSUPPORTED_TRACK", f"MIDI track {index} '{name}' retained raw, not treated as guitar notes.")
            continue
        split = {d: dict(section=d + ("Single" if instrument == "five_fret_lead_guitar" else "_" + name.replace(" ", "_")),
                         difficulty=d, instrument=instrument, source_track=name, notes=[], modifiers=[], special_events=[]) for d in DIFFICULTIES}
        shared, unknown = [], []
        seen = set()
        for event, duration in sorted(pairs, key=lambda pair: (pair[0]["tick"], pair[0]["order"])):
            pitch = event["data"][0]
            record = dict(**clock.span(event["tick"], duration, None), source_order=event["order"],
                          source_track_index=index, source_channel=event["channel"], source_pitch=pitch,
                          source_velocity=event["data"][1], source_line=None)
            found = False
            for d, base in zip(DIFFICULTIES, (60, 72, 84, 96)):
                delta = pitch - base
                if 0 <= delta <= 4 or (delta == -1 and enhanced):
                    key = d, event["tick"], delta
                    if key in seen:
                        fail("MIDI_DUPLICATE_LANE", "Duplicate logical lane at one tick across MIDI channels.")
                    seen.add(key)
                    split[d]["notes"].append(dict(**record, lane=None if delta == -1 else delta,
                                                       source_lane=7 if delta == -1 else delta,
                                                       kind="open" if delta == -1 else "fretted"))
                    found = True
                    break
                if delta in (5, 6):
                    split[d]["modifiers"].append(dict(**record, kind="force_hopo" if delta == 5 else "force_strum", source_lane=pitch))
                    found = True
                    break
            if not found:
                if pitch in MARKERS:
                    shared.append(dict(**record, kind=MARKERS[pitch]))
                else:
                    unknown.append(dict(**record, kind="uninterpreted_midi_note"))
        for e in events:
            if "text" in e or e["type"] == "sysex":
                shared.append(dict(**e, time_us=checked_time(clock.time(e["tick"])), time_us_exact=rational(clock.time(e["tick"]))))
        for track in split.values():
            track["special_events"] = shared + unknown
            tracks.append(track)
        if unknown:
            diagnostic(warnings, "MIDI_UNKNOWN_PITCH", f"{name}: {len(unknown)} non-fret pitches preserved as uninterpreted events, never playable notes.")
        if shared or any(t["modifiers"] for t in split.values()):
            diagnostic(warnings, "MIDI_MARKERS_PREPARED", f"{name}: star-power/solo/forcing/tap/text markers retained; no gameplay semantics applied.")
        diagnostic(warnings, "MIDI_NATIVE_LENGTHS", f"{name}: raw note lengths preserved, including short MIDI releases; no sustain cutoff, chord snapping or automatic HOPO rules applied.")
    if not any(t["notes"] for t in tracks):
        fail("NO_SUPPORTED_NOTES", "No notes in a recognized five-fret MIDI instrument track. Name lead guitar PART GUITAR (or T1 GEMS).")
    diagnostic(warnings, "NO_RUNTIME_BINDING", "Normalized MIDI data is not connected to the existing demo or its audio.")
    return dict(schema_version="gba-song-data-v1", schema_revision=2, source_format="midi", midi_format=fmt,
                source_name=source_name, resolution=resolution, metadata={},
                timing=dict(unit="microseconds", offset_seconds="0", offset_explicit=False,
                            offset_policy="audio_origin_time = tempo_time + chart_offset + song_ini_delay",
                            rounding="nearest_integer_half_away_from_zero; duration = rounded_end - rounded_start"),
                tempo_map=points, time_signatures=signatures, anchors=[], tracks=tracks,
                global_events=global_events, unsupported_sections=unsupported,
                midi_source_tracks=raw_tracks)
