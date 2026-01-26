"""Golden test for trie spell checker."""
from __future__ import annotations


# --- Trie implementation (from trie.py) ---

ascii_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class TrieNode:
    def __init__(self):
        self.is_word = False
        self.s = dict([(c, None) for c in ascii_letters])


def add(T, w, i=0):
    """Add a word to the trie"""
    if T is None:
        T = TrieNode()
    if i == len(w):
        T.is_word = True
    else:
        T.s[w[i]] = add(T.s[w[i]], w, i + 1)
    return T


def Trie(S):
    """Build the trie for the words in the dictionary S"""
    T = None
    for w in S:
        T = add(T, w)
    return T


def spell_check(T, w):
    """Spellchecker - find a closest word from the dictionary"""
    assert T is not None
    dist = 0
    while True:
        u = search(T, dist, w)
        if u is not None:
            return u
        dist += 1


def search(T, dist, w, i=0):
    """Searches for w[i:] in trie T with distance at most dist"""
    if i == len(w):
        if T is not None and T.is_word and dist == 0:
            return ""
        else:
            return None
    if T is None:
        return None
    f = search(T.s[w[i]], dist, w, i + 1)  # matching
    if f is not None:
        return w[i] + f
    if dist == 0:
        return None
    for c in ascii_letters:
        f = search(T.s[c], dist - 1, w, i)      # insertion
        if f is not None:
            return c + f
        f = search(T.s[c], dist - 1, w, i + 1)  # substitution
        if f is not None:
            return c + f
    return search(T, dist - 1, w, i + 1)        # deletion


# --- Tests ---

# Build a simple dictionary
words = ["hello", "help", "world", "word", "work", "test"]
T = Trie(words)

# Test spell check with exact matches
result1 = spell_check(T, "hello")
print(f"spell_check(hello): {result1}")  # Should be "hello"

result2 = spell_check(T, "world")
print(f"spell_check(world): {result2}")  # Should be "world"

# Test spell check with one character error
result3 = spell_check(T, "helo")
print(f"spell_check(helo): {result3}")  # Should find "hello"

result4 = spell_check(T, "wold")
print(f"spell_check(wold): {result4}")  # Should find "word" or "world"

# Test spell check with substitution
result5 = spell_check(T, "tist")
print(f"spell_check(tist): {result5}")  # Should find "test"

print("trie tests passed")
