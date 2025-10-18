# core_test_temporal.py
import sys
import os
from datetime import datetime, timedelta

# --- Setup import path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.ontology import Ontology
from core.temporal import TemporalRelation, TimeInterval
from core.truth import TruthState, TruthValue

print("\n=== TemporalRelation Tests ===")

# --- Setup Ontology ---
onto = Ontology()
THOMAS = onto.add_entity("THOMAS", word_type="NOUN", description="A person named Thomas")
A_MEETING = onto.add_entity("A_MEETING", word_type="NOUN", description="A scheduled meeting")
ATTENDS = onto.add_predicate("ATTENDS")

# Add TemporalRelation
THOMAS_ATTENDS_A_MEETING = onto.add_temporal_relation(
    ATTENDS,
    roles={"subject": THOMAS, "object": A_MEETING},
)

start_time = datetime.now()
duration = timedelta(minutes=30)
end_time=start_time + duration

THOMAS_ATTENDS_A_MEETING.add_interval(TimeInterval(start_time, end_time), TruthValue(TruthState.TRUE))

print(f"Initial relation: {THOMAS_ATTENDS_A_MEETING}")

# --- Test active queries ---
assert THOMAS_ATTENDS_A_MEETING.truth_value_at(start_time) == TruthState.TRUE
assert THOMAS_ATTENDS_A_MEETING.truth_value_at(start_time + timedelta(minutes=15)) == TruthState.TRUE
assert THOMAS_ATTENDS_A_MEETING.truth_value_at(start_time - timedelta(minutes=5)) == TruthState.UNKNOWN  # default_truth

# --- Add a past interval ---
past_start = start_time - timedelta(days=1)
past_end = past_start + timedelta(hours=1)
THOMAS_ATTENDS_A_MEETING.add_interval(TimeInterval(past_start, past_end), TruthValue(TruthState.TRUE))

assert THOMAS_ATTENDS_A_MEETING.truth_value_at(past_start + timedelta(minutes=30)) == TruthState.TRUE
assert THOMAS_ATTENDS_A_MEETING.truth_value_at(past_start - timedelta(minutes=5)) == TruthState.UNKNOWN  # default_truth

# --- Add a future interval ---
future_start = datetime.now() + timedelta(days=1)
future_end = future_start + timedelta(hours=2)
THOMAS_ATTENDS_A_MEETING.add_interval(TimeInterval(future_start, future_end), TruthValue(TruthState.TRUE))

assert THOMAS_ATTENDS_A_MEETING.truth_value_at(future_start - timedelta(minutes=1)) == TruthState.UNKNOWN  # default_truth
assert THOMAS_ATTENDS_A_MEETING.truth_value_at(future_start + timedelta(minutes=30)) == TruthState.TRUE

# --- Verify all intervals are stored correctly ---
print("\nAll intervals in THOMAS_ATTENDS_A_MEETING:")
for interval, tv in THOMAS_ATTENDS_A_MEETING.interval_truths.items():
    print(f"  {interval} -> {tv}")

# --- Overlapping interval test ---
print("\n=== Overlapping Interval Test ===")
try:
    # This interval overlaps the first interval we created
    overlapping_start = start_time + timedelta(minutes=15)
    overlapping_end = start_time + timedelta(minutes=45)
    THOMAS_ATTENDS_A_MEETING.add_interval(TimeInterval(overlapping_start, overlapping_end))
except ValueError as e:
    print(f"Caught expected error: {e}")

# --- Test default_truth with different value ---
DEFAULT_FALSE = TruthValue(TruthState.FALSE)
tr_false_default = TemporalRelation(
    predicate=ATTENDS,
    roles={"subject": THOMAS, "object": A_MEETING},
    default_truth=DEFAULT_FALSE
)

print("\nDefault FALSE test:")
assert tr_false_default.truth_value_at(datetime.now() - timedelta(days=100)) == TruthState.FALSE

print("\n✅ All TemporalRelation interval tests passed!\n")
