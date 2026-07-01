from engine.srt_utils import parse_srt_text, compose_srt, merge_short_entries, _parse_ts

SAMPLE = """1
00:00:01,000 --> 00:00:04,000
何してるの？

2
00:00:05,000 --> 00:00:08,000
見てないよ

3
00:00:09,000 --> 00:00:12,000
そうなの？
"""


def test_parse_srt_basic():
    entries = parse_srt_text(SAMPLE)
    assert len(entries) == 3
    assert entries[0] == (1, "00:00:01,000 --> 00:00:04,000", "何してるの？")
    assert entries[2] == (3, "00:00:09,000 --> 00:00:12,000", "そうなの？")


def test_parse_srt_empty():
    assert parse_srt_text("") == []
    assert parse_srt_text("   ") == []


def test_parse_srt_invalid():
    raw = "garbage\n\n1\n00:00:01,000 --> 00:00:02,000\nhello"
    entries = parse_srt_text(raw)
    assert len(entries) == 1
    assert entries[0] == (1, "00:00:01,000 --> 00:00:02,000", "hello")


def test_compose_roundtrip():
    entries = parse_srt_text(SAMPLE)
    composed = compose_srt(entries)
    re_parsed = parse_srt_text(composed)
    assert entries == re_parsed


def test_merge_short_entries():
    entries = [
        (1, "00:00:01,000 --> 00:00:02,000", "あ"),
        (2, "00:00:02,100 --> 00:00:03,000", "い"),
        (3, "00:00:10,000 --> 00:00:12,000", "長いテキスト"),
    ]
    merged = merge_short_entries(entries)
    assert len(merged) == 2
    assert merged[0][2] == "あい"


def test_merge_noop():
    entries = [
        (1, "00:00:01,000 --> 00:00:04,000", "長いテキストです"),
        (2, "00:00:10,000 --> 00:00:12,000", "これも長い"),
    ]
    merged = merge_short_entries(entries)
    assert merged == entries


def test_merge_time_dense():
    entries = [
        (1, "00:00:01,000 --> 00:00:02,000", "長い文ですよね"),
        (2, "00:00:02,000 --> 00:00:04,000", "続きの文です"),
    ]
    merged = merge_short_entries(entries)
    assert len(merged) == 1
    assert merged[0][2] == "長い文ですよね続きの文です"


def test_merge_time_gap_too_large():
    entries = [
        (1, "00:00:01,000 --> 00:00:02,000", "長い文です"),
        (2, "00:00:03,000 --> 00:00:04,000", "これも長い"),
    ]
    merged = merge_short_entries(entries)
    assert len(merged) == 2  # gap 1s > time_merge_gap 0.2s


def test_parse_ts():
    assert _parse_ts("00:01:30,500") == 90.5
    assert _parse_ts("00:00:00,000") == 0.0
    assert _parse_ts("01:00:00,000") == 3600.0
