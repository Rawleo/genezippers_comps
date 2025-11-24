import sys
from pathlib import Path
# Ensure project root (biocompress_1) is first on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compressor import encode, process

def test_encode_with_empty_buffer():
    processed = ("11", "base", 1)
    buffer = []
    result = encode(processed, buffer)
    # It should start a new buffer with the processed item
    assert result == [processed]

def test_encode_with_matching_kinds():
    processed = ("10", "base", 1)
    buffer = [("11", "base", 1), ("00", "base", 1)]
    result = encode(processed, buffer)
    # It should append to the existing buffer
    assert result == [("11", "base", 1), ("00", "base", 1), ("10", "base", 1)]

def test_encode_with_different_kinds():
    processed = ("11011", "factor", 5)
    buffer = [("11", "base", 1), ("01", "base", 1)]
    result = encode(processed, buffer)
    # It should start a new buffer with the processed item
    assert result == [processed]

def test_process_factor_empty_tree(mock_content, fresh_tree, monkeypatch):
    mock_content
    tree = fresh_tree(2) 
    processed = process(0)
    print(tree.a_branch.positions)
    print(tree.a_branch.c_branch.positions)
    assert tree.a_branch.positions == [0]
    assert processed == ("11", "base", 1)
