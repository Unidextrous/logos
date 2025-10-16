# test_temporal.py
import sys
import os
from datetime import datetime, timedelta

# --- Setup import path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology
from core.temporal import TemporalRelation, TimeInterval

print("\n=== TemporalRelation Tests ===")

# --- Setup Ontology ---
onto = Ontology()
THOMAS = onto.add_entity("THOMAS", word_type="NOUN", description="A person named Thomas")
A_MEETING = onto.add_entity("A_MEETING", word_type="NOUN", description="A scheduled meeting")
ATTENDS = onto.add_predicate("ATTENDS")

# --- Create a TemporalRelation with one interval ---
start = datetime.now()
duration = timedelta(minutes=30)
THOMAS_ATTENDS_A_MEETING = onto.add_temporal_relation(
    ATTENDS,
    roles={"subject": THOMAS, "object": A_MEETING},
    start_time=start,
    end_time=start + duration
)

print(f"Initial relation: {THOMAS_ATTENDS_A_MEETING}")

# --- Test active queries ---
assert THOMAS_ATTENDS_A_MEETING.is_active_at(start)
assert THOMAS_ATTENDS_A_MEETING.is_active_at(start + timedelta(minutes=15))
assert not THOMAS_ATTENDS_A_MEETING.is_active_at(start - timedelta(minutes=5))

# --- Add a past interval ---
past_start = start - timedelta(days=1)
past_end = past_start + timedelta(hours=1)
THOMAS_ATTENDS_A_MEETING.add_interval(past_start, past_end)

assert THOMAS_ATTENDS_A_MEETING.is_active_at(past_start + timedelta(minutes=30))
assert not THOMAS_ATTENDS_A_MEETING.is_active_at(past_start - timedelta(minutes=5))

# --- Add a future interval ---
future_start = datetime.now() + timedelta(days=1)
future_end = future_start + timedelta(hours=2)
THOMAS_ATTENDS_A_MEETING.add_interval(future_start, future_end)

assert not THOMAS_ATTENDS_A_MEETING.is_active_at(future_start - timedelta(minutes=1))
assert THOMAS_ATTENDS_A_MEETING.is_active_at(future_start + timedelta(minutes=30))

# --- Verify all intervals are stored correctly ---
print("\nAll intervals in THOMAS_ATTENDS_A_MEETING:")
for interval in THOMAS_ATTENDS_A_MEETING.active_intervals:
    print(f"  {interval}")

# --- Overlapping interval test ---
print("\n=== Overlapping Interval Test ===")

try:
    # This interval overlaps the first interval we created
    overlapping_start = start + timedelta(minutes=15)
    overlapping_end = start + timedelta(minutes=45)
    THOMAS_ATTENDS_A_MEETING.add_interval(overlapping_start, overlapping_end)
except ValueError as e:
    print(f"Caught expected error: {e}")

print("\n✅ All TemporalRelation interval tests passed!\n")
