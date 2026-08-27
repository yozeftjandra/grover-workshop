# Grover Workshop

Support package and notebooks for the Grover's algorithm hands-on session.

## Contents

- `grover_workshop/` — installable Python package providing oracle construction,
  a single-shot interference query, a progress metric, and the grading functions
  used by the notebooks' self-check exercises.
- `Grover_Workshop_template.ipynb` — the notebook participants work from during
  the session.
- `Grover_Workshop_solution.ipynb` — the same notebook with worked solutions.
- `pyproject.toml` / `requirements.txt` — package metadata and dependencies.

## Setup

Both notebooks install everything they need in their first cell:

```
!pip install qiskit pylatexenc
!pip install git+https://github.com/yozeftjandra/grover-workshop.git -q
```

To set up an environment yourself instead (e.g. to run the notebooks locally
rather than in Colab):

```bash
pip install -r requirements.txt
pip install git+https://github.com/yozeftjandra/grover-workshop.git
```

`requirements.txt` pins `qiskit>=1.3` — the package uses `MCMTGate`
(`qiskit.circuit.library`), which was only introduced in qiskit 1.3.

## Package overview

- **`oracles.py`** — builds no-ancilla, phase-kickback oracles from a list of
  marked bitstrings (`build_quantum_oracle`), plus two secret oracles used in
  the graded exercises (`get_secret_oracle_1`, `get_secret_oracle_2`). Marked
  bitstrings are given in ordinary left-to-right reading order; Qiskit's
  bit-order reversal is handled internally.
- **`query.py`** — `quantum_query` answers "is this bitstring marked?" for a
  single guess, by interfering the guess against a reference state and
  measuring which one "wins".
- **`metrics.py`** — `angle_to_marked` computes the exact statevector angle
  between the current state and the marked-state subspace, for tracking
  progress toward (and past) the optimal number of Grover iterations.
- **`grading.py`** — `grade_<section>_<step>_...` functions, one per
  self-check exercise, matched by name to the notebook section they grade.
  Section 5 and Section 7 graders are verbose (known, non-secret oracle,
  or no instructor present); Section 6.2/6.3 graders are deliberately
  minimal, since they check against the two secret oracles and revealing
  detail would defeat the exercise.

`grover_workshop._secrets` holds the two secret oracles' marked states and is
intentionally not part of the public API — participants aren't meant to
import it directly.

## Session structure

The session is scoped to one hour. Hands-on oracle construction is optional,
self-sufficient content (Section 7) rather than a core live activity; the
protected core is building Grover layer-by-layer against a known example
oracle (Section 5) and the graded secret-oracle exercise (Section 6).

| # | Segment | Mode |
|---|---|---|
| 1 | Intro to oracle search problem | Brief |
| 2 | Classical oracle worst-case | Shown (not participatory) |
| 3 | Quantum oracle demo | Shown, no hands-on |
| 4 | Anatomy of Grover's algorithm | Explained |
| 5 | Build Grover layer-by-layer, measure per layer (example oracle) | Hands-on, core |
| 6 | Exercise: guess secret oracle strings (graded via package) | Hands-on, core |
| 7 | Oracle design | Deferred — self-sufficient notebook section |

