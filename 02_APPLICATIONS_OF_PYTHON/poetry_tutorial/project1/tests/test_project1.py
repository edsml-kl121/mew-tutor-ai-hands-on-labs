# tests/test_my_project.py

def test_addition():
    assert 1 + 1 == 2

def test_numpy_import():
    try:
        import numpy as np
        assert np.array([1, 2, 3]).sum() == 6
    except ImportError:
        assert False, "numpy is not installed"