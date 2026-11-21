"""Unit tests for session derivation, sub-2s debouncing, and daily aggregation math."""
from datetime import datetime, timedelta, timezone
import pytest
from app.modules.usage_processing.service import (
    calculate_active_screen_time,
    debounce_app_intervals,
    format_seconds_to_human,
)


def test_format_seconds_to_human():
    """Verify conversion of raw seconds into 'Xh Ym' string."""
    assert format_seconds_to_human(0) == "0m"
    assert format_seconds_to_human(59) == "0m"
    assert format_seconds_to_human(60) == "1m"
    assert format_seconds_to_human(3600) == "1h 0m"
    assert format_seconds_to_human(5400) == "1h 30m"
    assert format_seconds_to_human(12600) == "3h 30m"


def test_debounce_app_intervals_under_2s():
    """Verify micro-interruptions under 2 seconds are merged into a continuous session."""
    t0 = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    intervals = [
        # Session 1: 10:00:00 - 10:05:00 (300s)
        {"package_name": "com.slack", "start_time": t0, "end_time": t0 + timedelta(seconds=300), "duration_seconds": 300},
        # Interruption of 1.5s (under 2s threshold)
        # Session 2: 10:05:01.5 - 10:10:00 (298.5s -> 298s)
        {
            "package_name": "com.slack",
            "start_time": t0 + timedelta(seconds=301.5),
            "end_time": t0 + timedelta(seconds=600),
            "duration_seconds": 298,
        },
    ]

    merged = debounce_app_intervals(intervals, debounce_threshold_seconds=2.0)
    assert len(merged) == 1
    assert merged[0]["package_name"] == "com.slack"
    assert merged[0]["duration_seconds"] >= 598


def test_debounce_app_intervals_over_2s_preserved_as_discrete():
    """Verify gaps greater than 2 seconds remain distinct discrete sessions."""
    t0 = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    intervals = [
        {"package_name": "com.slack", "start_time": t0, "end_time": t0 + timedelta(seconds=120), "duration_seconds": 120},
        # 10 second gap
        {"package_name": "com.slack", "start_time": t0 + timedelta(seconds=130), "end_time": t0 + timedelta(seconds=200), "duration_seconds": 70},
    ]

    merged = debounce_app_intervals(intervals, debounce_threshold_seconds=2.0)
    assert len(merged) == 2


def test_calculate_active_screen_time():
    """Verify active screen-unlocked intervals are summed correctly."""
    t0 = datetime(2026, 11, 20, 10, 0, 0, tzinfo=timezone.utc)
    screen_events = [
        {"event_type": "SCREEN_ON", "timestamp": t0},
        {"event_type": "USER_UNLOCKED", "timestamp": t0 + timedelta(seconds=2)},
        {"event_type": "SCREEN_OFF", "timestamp": t0 + timedelta(seconds=602)},
    ]
    # Active unlocked: 602 - 2 = 600s, 1 unlock
    total_screen_time, total_unlocks = calculate_active_screen_time(screen_events)
    assert total_screen_time == 600
    assert total_unlocks == 1
