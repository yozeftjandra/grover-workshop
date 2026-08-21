"""grover_workshop

Support package for the Grover's algorithm hands-on workshop (HO#02).

Provides oracle construction/retrieval, a single-shot interference query,
a metric for tracking progress toward the marked subspace, and grading
functions for the workshop's self-check exercises.

Grading functions are named `grade_<section>_<step>_...` to match the
notebook section they belong to.
"""

from .oracles import (
    build_quantum_oracle,
    get_secret_oracle_1,
    get_secret_oracle_2,
    EXAMPLE_MARKED_STATES,
)
from .query import quantum_query
from .metrics import angle_to_marked
from .grading import (
    GradeResult,
    grade_5_1_superposition,
    grade_5_2_single_layer,
    grade_5_3_readout,
    grade_5_4_iteration_count,
    grade_5_5_full_run,
    grade_6_1_query_intro,
    grade_6_2_secret_oracle,
    grade_6_3_bonus_discovery,
    grade_7_3_step_a,
    grade_7_3_step_a_exercise,
    grade_7_4_step_b,
    grade_7_5_step_c,
)

__all__ = [
    "build_quantum_oracle",
    "get_secret_oracle_1",
    "get_secret_oracle_2",
    "EXAMPLE_MARKED_STATES",
    "quantum_query",
    "angle_to_marked",
    "GradeResult",
    "grade_5_1_superposition",
    "grade_5_2_single_layer",
    "grade_5_3_readout",
    "grade_5_4_iteration_count",
    "grade_5_5_full_run",
    "grade_6_1_query_intro",
    "grade_6_2_secret_oracle",
    "grade_6_3_bonus_discovery",
    "grade_7_3_step_a",
    "grade_7_3_step_a_exercise",
    "grade_7_4_step_b",
    "grade_7_5_step_c",
]
