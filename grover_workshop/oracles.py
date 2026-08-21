"""Oracle construction utilities for the Grover workshop.

All oracles built here use the no-ancilla, phase-kickback construction:
for each marked bitstring, the qubits corresponding to a '0' in the
(bit-order-reversed) target are sandwiched between X gates around a
multi-controlled Z gate. This flips the sign of exactly the marked basis
states and leaves every other basis state untouched.
"""

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMTGate, ZGate

from . import _secrets

# The fixed example oracle used throughout Sections 3, 5, and 7.
EXAMPLE_MARKED_STATES = ["1101", "0001"]


def build_quantum_oracle(marked_states, name="Oracle", draw_circuit=False):
    """Build a no-ancilla, phase-kickback oracle marking the given bitstrings.

    Parameters
    ----------
    marked_states : list[str]
        Bitstrings to mark, all of the same length. Pass states in the
        usual left-to-right reading order (e.g. "1101" means qubit 3 = 1,
        qubit 2 = 1, qubit 1 = 0, qubit 0 = 1) -- the Qiskit bit-order
        reversal is handled internally.
    name : str
        Name attached to the resulting gate (shown in circuit diagrams).
    draw_circuit : bool
        If True, draws and displays the constructed circuit before it is
        converted to a gate.

    Returns
    -------
    qiskit.circuit.Gate
    """
    if not marked_states:
        raise ValueError("marked_states must contain at least one bitstring")
    num_qubits = len(marked_states[0])
    if not all(len(s) == num_qubits for s in marked_states):
        raise ValueError("All marked states must have the same length")
    if "0" * num_qubits in marked_states:
        raise ValueError(
            "This construction cannot mark the all-zeros state"
        )

    qc = QuantumCircuit(num_qubits)
    for target in marked_states:
        rev_target = target[::-1]
        zero_inds = [ind for ind in range(num_qubits) if rev_target[ind] == "0"]

        if zero_inds:
            qc.x(zero_inds)
        if num_qubits == 1:
            qc.z(0)
        else:
            qc.compose(MCMTGate(ZGate(), num_qubits - 1, 1), inplace=True)
        if zero_inds:
            qc.x(zero_inds)

    if draw_circuit:
        from IPython.display import display
        display(qc.draw(output="mpl"))

    oracle = qc.to_gate()
    oracle.name = name
    return oracle


def get_secret_oracle_1(draw_circuit=False):
    """Return secret oracle 1 (8 qubits, M = 5), plus one revealed marked state.

    Used in Section 6.1 to reinforce the single-shot query mechanism from
    Section 3, and revisited in the Section 6.3 bonus exercise.

    Returns
    -------
    (qiskit.circuit.Gate, str)
        The oracle gate, and the single marked state revealed for
        Section 6.1. The other four marked states are not returned --
        finding them is the point of the Section 6.3 bonus exercise.
    """
    oracle = build_quantum_oracle(
        _secrets.ORACLE_1_MARKED_STATES,
        name="SecretOracle1",
        draw_circuit=draw_circuit,
    )
    return oracle, _secrets.ORACLE_1_REVEALED_STATE


def get_secret_oracle_2(draw_circuit=False):
    """Return secret oracle 2 (5 qubits, M = 3 declared), states hidden.

    Used as the main graded exercise in Section 6.2.

    Returns
    -------
    (qiskit.circuit.Gate, int)
        The oracle gate, and the declared number of marked states M.
        The marked states themselves are not returned.
    """
    oracle = build_quantum_oracle(
        _secrets.ORACLE_2_MARKED_STATES,
        name="SecretOracle2",
        draw_circuit=draw_circuit,
    )
    return oracle, len(_secrets.ORACLE_2_MARKED_STATES)
