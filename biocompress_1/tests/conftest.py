import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import AGCT_tree
import compressor

FAKE_CONTENT = "ACGTACGT"
TARGET_MODULES = [AGCT_tree, compressor]

@pytest.fixture
def set_height(monkeypatch):
    """
    Patch HEIGHT in all relevant modules for deterministic tests.
    """
    def _set(h: int):
        for module in TARGET_MODULES:
            monkeypatch.setattr(module, "HEIGHT", h, raising=False)
        return h
    return _set

@pytest.fixture
def fresh_tree(set_height, monkeypatch):
    """
    Build a fresh tree and apply it as TREE in all target modules.
    Also ensures HEIGHT is consistent.
    """
    def _build(height: int):
        set_height(height)
        tree = AGCT_tree.create_tree(height)
        for module in TARGET_MODULES:
            monkeypatch.setattr(module, "TREE", tree, raising=False)
        return tree
    return _build

@pytest.fixture
def mock_content(monkeypatch):
    """
    Set a fake DNA sequence as CONTENT in all target modules.
    Returns the same string.
    """
    for module in TARGET_MODULES:
        monkeypatch.setattr(module, "CONTENT", FAKE_CONTENT, raising=False)
    return FAKE_CONTENT


