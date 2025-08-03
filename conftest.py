import pytest
import sys
import os
from pathlib import Path

# Add the new layer directories to the Python path for tests
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "database-access"))
sys.path.insert(0, str(project_root / "database"))
sys.path.insert(0, str(project_root / "scripts"))

@pytest.fixture
def sample_fixture():
    return "Hello, World!"