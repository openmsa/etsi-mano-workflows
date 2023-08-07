import pytest
from python_mano_client.DescriptorGraphGeneration import DescriptorGraphGeneration

def test_basic():
    """
    Nothng.
    """
    DescriptorGraphGeneration("1.1.1.1", "80")
    assert True
