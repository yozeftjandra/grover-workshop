"""Grading functions for the Grover workshop.

Functions are named `grade_<section>_<step>_...` so each grader can be
matched to the notebook section it belongs to.

Section 5 and Section 6.1 graders are verbose -- they explain what went
wrong, since these sections use a known, non-secret oracle. Section 6.2
and 6.3 graders are deliberately minimal (correct / incorrect, with
partial-progress only for the bonus) since they grade against secret
oracles and revealing detail would defeat the exercise. Section 7 graders
are verbose, since Section 7 is self-sufficient with no instructor
present to informally confirm correctness.
"""

from dataclasses import dataclass, field
import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .oracles import EXAMPLE_MARKED_STATES
from .metrics import angle_to_marked
from .query import quantum_query
from . import _secrets


@dataclass
class GradeResult:
    """Result of a grading check.

    Attributes
    ----------
    correct : bool
    message : str
        Human-readable feedback. Verbose for most sections; deliberately
        terse for the secret-oracle sections (6.2, 6.3).
    details : dict
        Extra structured information (only populated for verbose graders).
    """
    correct: bool
    message: str
    details: dict = field(default_factory=dict)

    def __repr__(self):
        status = "PASS" if self.correct else "FAIL"
        return f"[{status}] {self.message}"


def _state_probs(circuit):
    sv = Statevector.from_instruction(circuit)
    return sv.probabilities_dict()


def _all_bitstrings(num_qubits):
    return [format(i, f"0{num_qubits}b") for i in range(2 ** num_qubits)]


# ---------------------------------------------------------------------------
# Section 5
# ---------------------------------------------------------------------------

def grade_5_1_superposition(qc, tolerance=0.05):
    """Check that `qc` prepares an equal superposition over all basis states."""
    probs = _state_probs(qc)
    n = qc.num_qubits
    expected = 1 / (2 ** n)
    deviating = [
        s for s in _all_bitstrings(n)
        if abs(probs.get(s, 0.0) - expected) > tolerance
    ]
    if not deviating:
        return GradeResult(
            True, "Equal superposition confirmed across all basis states."
        )
    return GradeResult(
        False,
        f"Distribution is not uniform -- {len(deviating)} basis state(s) deviate "
        f"from the expected {expected:.4f} probability by more than {tolerance}. "
        "Did you apply H to every qubit?",
        details={"deviating_states": deviating},
    )


def grade_5_2_single_layer(qc, marked_states=None, tolerance=0.05):
    """Check that one Grover layer has amplified the marked states."""
    marked_states = marked_states or EXAMPLE_MARKED_STATES
    probs = _state_probs(qc)
    p_marked = sum(probs.get(s, 0.0) for s in marked_states)
    n = qc.num_qubits
    baseline = len(marked_states) / (2 ** n)
    angle = angle_to_marked(qc, marked_states)

    if p_marked > baseline + tolerance:
        return GradeResult(
            True,
            f"Marked-state probability rose from a baseline of {baseline:.3f} to "
            f"{p_marked:.3f} -- amplification confirmed. Angle to the marked "
            f"subspace: {angle:.3f} rad.",
            details={"p_marked": p_marked, "baseline": baseline, "angle": angle},
        )
    return GradeResult(
        False,
        f"Marked-state probability is {p_marked:.3f}, not clearly above the "
        f"baseline of {baseline:.3f}. Did you compose exactly one layer of the "
        "Grover operator onto the superposed circuit?",
        details={"p_marked": p_marked, "baseline": baseline, "angle": angle},
    )


def grade_5_3_readout(guessed_states, dist, marked_states=None):
    """Check the participant's read-off of marked states from a histogram."""
    marked_states = marked_states or EXAMPLE_MARKED_STATES
    guessed_set, marked_set = set(guessed_states), set(marked_states)
    if guessed_set == marked_set:
        return GradeResult(True, "Correct -- both marked states identified.")
    missing, extra = marked_set - guessed_set, guessed_set - marked_set
    parts = []
    if missing:
        parts.append(f"missed {sorted(missing)}")
    if extra:
        parts.append(f"incorrectly included {sorted(extra)}")
    return GradeResult(
        False,
        "Not quite -- " + "; ".join(parts) + ". Look for the tallest bars in "
        "your histogram.",
        details={"missing": sorted(missing), "extra": sorted(extra)},
    )


def grade_5_4_iteration_count(n, marked_states=None, num_qubits=None):
    """Check a computed optimal iteration count."""
    marked_states = marked_states or EXAMPLE_MARKED_STATES
    num_qubits = num_qubits or len(marked_states[0])
    M, N = len(marked_states), 2 ** num_qubits
    expected = math.floor(math.pi / (4 * math.asin(math.sqrt(M / N))))
    if n == expected:
        return GradeResult(True, f"Correct -- optimal iteration count is {expected}.")
    return GradeResult(
        False,
        f"Got {n}, expected {expected}. Recall the formula "
        "floor(pi / (4 * arcsin(sqrt(M / N)))) -- double-check your M and N.",
        details={"expected": expected, "got": n},
    )


def grade_5_5_full_run(dist_optimal, dist_overrotated, marked_states=None):
    """Check that the optimal-depth run is sharper than the over-rotated one."""
    marked_states = marked_states or EXAMPLE_MARKED_STATES
    total_opt = sum(dist_optimal.values())
    total_over = sum(dist_overrotated.values())
    p_opt = sum(dist_optimal.get(s, 0) for s in marked_states) / total_opt
    p_over = sum(dist_overrotated.get(s, 0) for s in marked_states) / total_over

    if p_opt > p_over:
        return GradeResult(
            True,
            f"Confirmed -- marked-state probability at optimal depth ({p_opt:.3f}) "
            f"exceeds the over-rotated run ({p_over:.3f}). More layers is not "
            "always better.",
            details={"p_optimal": p_opt, "p_overrotated": p_over},
        )
    return GradeResult(
        False,
        f"Expected the optimal-depth run to beat the over-rotated run, but got "
        f"{p_opt:.3f} vs {p_over:.3f}. Double-check which distribution came from "
        "which circuit.",
        details={"p_optimal": p_opt, "p_overrotated": p_over},
    )


# ---------------------------------------------------------------------------
# Section 6
# ---------------------------------------------------------------------------

def grade_6_1_query_intro(result_correct, result_incorrect):
    """Check the two Section 6.1 query outcomes contrast as expected."""
    def p_one(dist):
        total = sum(dist.values())
        return dist.get("1", 0) / total if total else 0.0

    p_correct, p_incorrect = p_one(result_correct), p_one(result_incorrect)
    if p_correct > 0.9 and p_incorrect < 0.1:
        return GradeResult(
            True,
            f"Correct -- querying the revealed marked state gave a clearly "
            f"different outcome ({p_correct:.2f}) from the incorrect guess "
            f"({p_incorrect:.2f}).",
        )
    return GradeResult(
        False,
        f"The two query results don't contrast as expected (revealed state: "
        f"{p_correct:.2f}, incorrect guess: {p_incorrect:.2f}). Re-check that you "
        "queried the revealed state in the first run and a genuinely different "
        "bitstring in the second.",
        details={"p_correct": p_correct, "p_incorrect": p_incorrect},
    )


def grade_6_2_secret_oracle(guess):
    """Minimal-feedback grading against secret oracle 2. No detail revealed."""
    correct = set(guess) == set(_secrets.ORACLE_2_MARKED_STATES)
    return GradeResult(correct, "Correct." if correct else "Incorrect -- try again.")


def grade_6_3_bonus_discovery(guessed_states):
    """Minimal-feedback grading for the Section 6.3 bonus (secret oracle 1)."""
    guessed_set = set(guessed_states)
    marked_set = set(_secrets.ORACLE_1_MARKED_STATES)
    n_correct, total = len(guessed_set & marked_set), len(marked_set)
    correct = guessed_set == marked_set
    message = (
        f"Correct -- all {total} marked states found."
        if correct else f"Found {n_correct} of {total} marked states."
    )
    return GradeResult(correct, message, details={"n_correct": n_correct, "total": total})


# ---------------------------------------------------------------------------
# Section 7
# ---------------------------------------------------------------------------

def grade_7_3_step_a(qc, marked_state="1101"):
    """Check the manually-built Section 7.3 oracle for one fixed marked state."""
    num_qubits = len(marked_state)
    gate = qc.to_gate()

    p_marked = quantum_query(gate, marked_state, shots=1000).get("1", 0) / 1000
    if p_marked < 0.9:
        return GradeResult(
            False,
            f"Querying your circuit against '{marked_state}' did not behave like "
            "a marked state. Check your X-sandwich indices and the placement of "
            "the multi-controlled-Z gate.",
        )
    other_states = [s for s in _all_bitstrings(num_qubits) if s != marked_state][:3]
    for other in other_states:
        p_other = quantum_query(gate, other, shots=1000).get("1", 0) / 1000
        if p_other > 0.1:
            return GradeResult(
                False,
                f"Your circuit also marks '{other}', which it shouldn't. Check "
                "that your X gates only target the zero positions of the marked "
                "state.",
            )
    return GradeResult(
        True, f"Correct -- '{marked_state}' is marked and other states are not."
    )


def grade_7_3_step_a_exercise(qc, marked_state, num_qubits=None):
    """Check the Section 7.3b exercise (a different marked state / qubit count)."""
    return grade_7_3_step_a(qc, marked_state=marked_state)


def grade_7_4_step_b(build_oracle_single_fn):
    """Check a generalised single-marked-state oracle-building function."""
    test_cases = ["1101", "0001", "101", "11001"]
    for marked_state in test_cases:
        try:
            gate = build_oracle_single_fn(marked_state)
        except Exception as e:
            return GradeResult(
                False,
                f"Calling your function on '{marked_state}' raised "
                f"{type(e).__name__}: {e}",
            )
        p_marked = quantum_query(gate, marked_state, shots=1000).get("1", 0) / 1000
        if p_marked < 0.9:
            return GradeResult(
                False,
                f"Your function's oracle for '{marked_state}' does not mark it "
                "correctly. Check that it generalises your Step A logic (finding "
                "the zero positions programmatically) rather than assuming a "
                "fixed bitstring.",
            )
    return GradeResult(
        True,
        "Correct -- your function builds a valid oracle for any single marked "
        "state.",
    )


def grade_7_5_step_c(build_oracle_multi_fn):
    """Check a multi-marked-state oracle-building function, including the
    Section 3/5 example oracle for direct comparison."""
    test_cases = [EXAMPLE_MARKED_STATES, ["101", "010"], ["1111", "1010", "0110"]]
    for marked_states in test_cases:
        try:
            gate = build_oracle_multi_fn(marked_states)
        except Exception as e:
            return GradeResult(
                False,
                f"Calling your function on {marked_states} raised "
                f"{type(e).__name__}: {e}",
            )
        for state in marked_states:
            p_marked = quantum_query(gate, state, shots=1000).get("1", 0) / 1000
            if p_marked < 0.9:
                return GradeResult(
                    False,
                    f"Your function's oracle for {marked_states} does not mark "
                    f"'{state}' correctly.",
                )
    return GradeResult(
        True,
        "Correct -- your function correctly builds oracles for multiple marked "
        "states, including the same oracle used in Sections 3 and 5.",
    )
