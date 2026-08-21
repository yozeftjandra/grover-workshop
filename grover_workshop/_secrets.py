"""Internal data for the two secret oracles used in Section 6.

This module is intentionally not exported from the package's public API
(see __init__.py). Participants are not expected to import it directly --
doing so defeats the point of the exercise.
"""

# Secret oracle 1: 8 qubits, M = 5 marked states.
# One state is revealed to participants in Section 6.1. The remaining
# four stay hidden until the Section 6.3 bonus exercise.
ORACLE_1_NUM_QUBITS = 8
ORACLE_1_MARKED_STATES = [
    "01111101",
    "01110010",
    "01000111",
    "00110100",
    "00101100",
]
ORACLE_1_REVEALED_STATE = "00101100"

# Secret oracle 2: 5 qubits, M = 3 marked states.
# M is declared to participants; the marked states themselves stay hidden
# throughout Section 6.2.
ORACLE_2_NUM_QUBITS = 5
ORACLE_2_MARKED_STATES = ["00111", "00001", "10001"]
