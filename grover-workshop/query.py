"""Single-shot interference-based oracle query.

This implements the "is this state marked?" query used in Section 3 and
Section 6.1. A phase flip alone is not directly observable, so we
interfere the guessed state against a fixed reference state and measure
which one "wins": a marked guess produces a different measurement
pattern than an unmarked one.
"""

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def quantum_query(oracle, bitstring_guess, draw_circuit=False, shots=1_000, seed=None):
    """Query whether `bitstring_guess` is marked by `oracle`.

    Parameters
    ----------
    oracle : qiskit.circuit.Gate
        An oracle built by build_quantum_oracle (or a secret oracle from
        get_secret_oracle_1 / get_secret_oracle_2).
    bitstring_guess : str
        The bitstring to test.
    draw_circuit : bool
        If True, draws and displays the constructed query circuit.
    shots : int
        Number of sampler shots.
    seed : int, optional
        Sampler seed, for reproducible shot outcomes.

    Returns
    -------
    dict
        Measurement counts. A guess that is marked will show up almost
        entirely as "1"; an unmarked guess will show up almost entirely
        as "0".
    """
    num_qubits = len(bitstring_guess)
    qc = QuantumCircuit(num_qubits, 1)

    rev_guess = bitstring_guess[::-1]
    one_inds = [i for i, bit in enumerate(rev_guess) if bit == "1"]

    if not one_inds:
        # Special case for an all-zero guess: use qubit 0 as the reference
        # and prepare (|00...0> + |11...1>) / sqrt(2) instead.
        ref_idx = 0
        qc.h(ref_idx)
        for i in range(1, num_qubits):
            qc.cx(ref_idx, i)
        qc.x(range(num_qubits))
    else:
        ref_idx = one_inds[0]
        qc.h(ref_idx)
        for idx in one_inds[1:]:
            qc.cx(ref_idx, idx)

    qc.barrier()
    qc = qc.compose(oracle)
    qc.barrier()

    if one_inds:
        for idx in reversed(one_inds[1:]):
            qc.cx(ref_idx, idx)
        qc.h(ref_idx)
    else:
        qc.x(range(num_qubits))
        for i in reversed(range(1, num_qubits)):
            qc.cx(ref_idx, i)
        qc.h(ref_idx)

    qc.measure(ref_idx, 0)

    if draw_circuit:
        from IPython.display import display
        display(qc.draw(output="mpl"))

    sampler = StatevectorSampler(seed=seed) if seed is not None else StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    dist = result[0].data.c.get_counts()
    return dist
