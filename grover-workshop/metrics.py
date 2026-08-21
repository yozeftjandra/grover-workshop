"""Metrics for tracking Grover's algorithm progress.

angle_to_marked computes the angle (in radians) between the current
quantum state and the marked-state subspace, using the exact statevector.
This angle shrinks toward zero as the algorithm approaches the optimal
number of iterations, then grows again past that point (over-rotation).
"""

import math

from qiskit.quantum_info import Statevector


def angle_to_marked(circuit, marked_states):
    """Compute the angle between the circuit's state and the marked subspace.

    Parameters
    ----------
    circuit : qiskit.QuantumCircuit
        A circuit *without* measurement. The angle is a statevector
        property and cannot be recovered from measurement counts alone.
    marked_states : list[str]
        The marked bitstrings, in the same left-to-right reading order
        used elsewhere in this package.

    Returns
    -------
    float
        The angle (in radians) between the current state and the
        marked-state subspace vector |beta>. This is 0 when the state
        lies entirely in the marked subspace, and pi/2 when it lies
        entirely in the unmarked subspace.
    """
    sv = Statevector.from_instruction(circuit)
    probs = sv.probabilities_dict()
    p_marked = sum(probs.get(s, 0.0) for s in marked_states)
    p_marked = min(max(p_marked, 0.0), 1.0)  # clamp floating-point noise
    return math.acos(math.sqrt(p_marked))
