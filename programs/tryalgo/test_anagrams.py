"""Golden test for anagrams algorithm."""
from __future__ import annotations


# --- Anagrams function (from anagrams.py) ---

def anagrams(S):
    """group a set of words into anagrams

    :param S: set of strings
    :returns: list of lists of strings

    :complexity:
        O(n k log k) in average, for n words of length at most k.
        O(n^2 k log k) in worst case due to the usage of a dictionary.
    """
    d = {}                         # maps s to list of words with signature s
    for word in S:                 # group words according to the signature
        s = ''.join(sorted(word))  # calculate the signature
        if s in d:
            d[s].append(word)      # append a word to an existing signature
        else:
            d[s] = [word]          # add a new signature and its first word
    # -- extract anagrams, ignoring anagram groups of size 1
    return [d[s] for s in d if len(d[s]) > 1]


# --- Tests ---

# Test case 1: Words with anagrams
words1 = ["cat", "act", "dog", "god", "tac"]
result1 = anagrams(words1)
# Sort the results for consistent output
result1_sorted = sorted([sorted(group) for group in result1])
# Print number of groups and words to avoid repr differences
print(f"anagrams1 groups: {len(result1_sorted)}")
print(f"anagrams1 group0: {' '.join(result1_sorted[0])}")
print(f"anagrams1 group1: {' '.join(result1_sorted[1])}")

# Test case 2: No anagrams
words2 = ["apple", "banana", "cherry"]
result2 = anagrams(words2)
print(f"anagrams2 count: {len(result2)}")

# Test case 3: All same anagrams
words3 = ["ab", "ba", "ab", "ba"]
result3 = anagrams(words3)
print(f"anagrams3 count: {len(result3)}")

# Test case 4: More complex
words4 = ["listen", "silent", "hello", "world", "enlist"]
result4 = anagrams(words4)
result4_sorted = sorted([sorted(group) for group in result4])
print(f"anagrams4 groups: {len(result4_sorted)}")
print(f"anagrams4 group0: {' '.join(result4_sorted[0])}")

print("anagrams tests passed")
