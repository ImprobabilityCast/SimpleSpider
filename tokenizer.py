# Tokenizer module

from collections import deque

_removeTokens = frozenset(["\n", "\r", "\t", " "])
_breakOnTokens = frozenset(["<", ">", "?", "!", "/", "-", "\"", "'", "\\", "="])

def _nextTokenOrTrash(text, idx):
    pos = idx
    isToken = text[idx] in _removeTokens
    while (pos < len(text) and (isToken == (text[pos] in _removeTokens))
            and text[pos] not in _breakOnTokens):
        pos += 1
    if pos == idx:
        pos += 1
    return text[idx:pos]

def tokenize(text):
    result = deque()
    idx = 0
    while idx < len(text):
        token = _nextTokenOrTrash(text, idx)
        idx += len(token)
        if token[0] not in _removeTokens:
            result.append(token)
    return result
