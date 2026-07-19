"""Test fixtures."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "seat_satisfaction": np.random.rand(n) * 5 + 5,
        "glossiness": np.random.rand(n) * 10,
        "softness": np.random.rand(n) * 5 + 5,
        "abrasion_resistance": np.random.rand(n) * 100,
        "material_type": np.random.choice(["A", "B", "C"], n),
        "production_batch": np.random.choice(["B001", "B002", "B003"], n),
    })
