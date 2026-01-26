"""Golden test for roman number conversion."""
from __future__ import annotations


# --- Roman numbers functions (from roman_numbers.py) ---

roman = [['', 'I', 'II', 'III', 'IV',  'V',   'VI',  'VII', 'VIII', 'IX'],
         ['', 'X', 'XX', 'XXX', 'XL',  'L',   'LX',  'LXX', 'LXXX', 'XC'],
         ['', 'C', 'CC', 'CCC', 'CD',  'D',   'DC',  'DCC', 'DCCC', 'CM'],
         ['', 'M', 'MM', 'M'*3, 'M'*4, 'M'*5, 'M'*6, 'M'*7, 'M'*8,  'M'*9]]


def roman2int(s):
    """Decode roman number

    :param s: string representing a roman number between 1 and 9999
    :returns: the decoded roman number
    """
    val = 0
    pos10 = 1000
    beg = 0
    for pos in range(3, -1, -1):
        for digit in range(9, -1, -1):
            r = roman[pos][digit]
            if s.startswith(r, beg):
                beg += len(r)
                val += digit * pos10
                break
        pos10 //= 10
    return val


def int2roman(val):
    """Code roman number

    :param val: integer between 1 and 9999
    :returns: the corresponding roman number
    """
    s = ''
    pos10 = 1000
    for pos in range(3, -1, -1):
        digit = val // pos10
        s += roman[pos][digit]
        val %= pos10
        pos10 //= 10
    return s


# --- Tests ---

# Test basic numbers
print(f"int2roman(1): {int2roman(1)}")      # I
print(f"int2roman(4): {int2roman(4)}")      # IV
print(f"int2roman(5): {int2roman(5)}")      # V
print(f"int2roman(9): {int2roman(9)}")      # IX
print(f"int2roman(10): {int2roman(10)}")    # X
print(f"int2roman(40): {int2roman(40)}")    # XL
print(f"int2roman(50): {int2roman(50)}")    # L
print(f"int2roman(90): {int2roman(90)}")    # XC
print(f"int2roman(100): {int2roman(100)}")  # C
print(f"int2roman(500): {int2roman(500)}")  # D
print(f"int2roman(1000): {int2roman(1000)}")  # M

# Test complex numbers
print(f"int2roman(1984): {int2roman(1984)}")  # MCMLXXXIV
print(f"int2roman(2024): {int2roman(2024)}")  # MMXXIV
print(f"int2roman(3999): {int2roman(3999)}")  # MMMCMXCIX

# Test roman2int
print(f"roman2int(I): {roman2int('I')}")      # 1
print(f"roman2int(IV): {roman2int('IV')}")    # 4
print(f"roman2int(IX): {roman2int('IX')}")    # 9
print(f"roman2int(XLII): {roman2int('XLII')}")  # 42
print(f"roman2int(MCMLXXXIV): {roman2int('MCMLXXXIV')}")  # 1984
print(f"roman2int(MMXXIV): {roman2int('MMXXIV')}")  # 2024

# Test roundtrip
for n in [1, 42, 100, 999, 1984, 2024, 3999]:
    r = int2roman(n)
    back = roman2int(r)
    print(f"roundtrip({n}): {str(n == back)}")

print("roman_numbers tests passed")
