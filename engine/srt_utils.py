import re
import pathlib


def parse_srt_text(raw):
    blocks = re.split(r"\n\n+", raw.strip())
    entries = []
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0])
            entries.append((idx, lines[1], "\n".join(lines[2:])))
        except ValueError:
            continue
    return entries


def parse_srt(path):
    raw = pathlib.Path(path).read_text(encoding="utf-8")
    return parse_srt_text(raw)


def compose_srt(entries):
    return "\n\n".join(f"{i}\n{t}\n{x}" for i, t, x in entries)


def _parse_ts(ts):
    h, m, s = ts.replace(",", ".").split(":")
    return float(h) * 3600 + float(m) * 60 + float(s)


def merge_short_entries(entries, max_len=3, max_gap=0.5, time_merge_gap=0.2):
    if not entries:
        return entries
    merged = []
    buf = [entries[0]]
    for e in entries[1:]:
        last = buf[-1]
        last_parts = last[1].split(" --> ")
        e_parts = e[1].split(" --> ")
        last_end = _parse_ts(last_parts[1])
        cur_start = _parse_ts(e_parts[0])
        gap = cur_start - last_end

        should_merge = False
        if gap <= time_merge_gap:
            should_merge = True
        elif len(last[2]) <= max_len and len(e[2]) <= max_len and gap <= max_gap:
            should_merge = True

        if should_merge:
            new_time = last_parts[0] + " --> " + e_parts[1]
            new_text = last[2].rstrip() + e[2].rstrip()
            buf.append((buf[0][0], new_time, new_text))
            del buf[-2]
            continue
        merged.append(buf[0])
        buf = [e]
    merged.append(buf[0])
    return merged


def validate_srt(path):
    try:
        entries = parse_srt(path)
        if not entries:
            return False
        indices = [e[0] for e in entries]
        return len(indices) == len(set(indices))
    except Exception:
        return False
