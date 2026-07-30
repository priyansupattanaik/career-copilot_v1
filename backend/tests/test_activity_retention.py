"""Unit tests for the 5-activity retention policy (no live Supabase required)."""

from app.activity import MAX_ACTIVITY_EVENTS, activity_ids_to_delete


def test_max_activity_events_is_five():
    assert MAX_ACTIVITY_EVENTS == 5


def test_activity_ids_to_delete_keeps_newest_five():
    rows = [{"id": f"id-{i}"} for i in range(8)]  # newest first: id-0 … id-7
    stale = activity_ids_to_delete(rows, keep=5)
    assert stale == ["id-5", "id-6", "id-7"]


def test_activity_ids_to_delete_noop_when_at_or_under_limit():
    rows = [{"id": f"id-{i}"} for i in range(5)]
    assert activity_ids_to_delete(rows, keep=5) == []
    assert activity_ids_to_delete(rows[:3], keep=5) == []
    assert activity_ids_to_delete([], keep=5) == []


def test_activity_ids_to_delete_skips_rows_without_id():
    rows = [{"id": "a"}, {"id": "b"}, {}, {"id": "c"}, {"id": "d"}, {"id": "e"}, {"id": "f"}]
    # keep 5 → drop index 5 and 6 when present
    stale = activity_ids_to_delete(rows, keep=5)
    assert "f" in stale
    assert "a" not in stale
