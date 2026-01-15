"""Tests for source map generation."""

from __future__ import annotations

import json

import pytest

from prescrypt.sourcemap import (
    Mapping,
    SourceMapGenerator,
    decode_vlq,
    encode_vlq,
    get_sourcemap_comment,
)


class TestVLQEncoding:
    """Test VLQ (Variable Length Quantity) encoding."""

    def test_encode_zero(self):
        """Zero encodes to 'A'."""
        assert encode_vlq(0) == "A"

    def test_encode_positive_small(self):
        """Small positive numbers."""
        assert encode_vlq(1) == "C"
        assert encode_vlq(2) == "E"
        assert encode_vlq(3) == "G"

    def test_encode_negative_small(self):
        """Small negative numbers."""
        assert encode_vlq(-1) == "D"
        assert encode_vlq(-2) == "F"
        assert encode_vlq(-3) == "H"

    def test_encode_larger_numbers(self):
        """Numbers requiring multiple characters."""
        # 16 requires continuation
        assert encode_vlq(16) == "gB"
        assert encode_vlq(100) == "oG"
        assert encode_vlq(-100) == "pG"

    def test_decode_zero(self):
        """Decode zero."""
        value, rest = decode_vlq("A")
        assert value == 0
        assert rest == ""

    def test_decode_positive(self):
        """Decode positive numbers."""
        value, rest = decode_vlq("C")
        assert value == 1
        assert rest == ""

        value, rest = decode_vlq("gB")
        assert value == 16
        assert rest == ""

    def test_decode_negative(self):
        """Decode negative numbers."""
        value, rest = decode_vlq("D")
        assert value == -1
        assert rest == ""

    def test_decode_with_remainder(self):
        """Decode with remaining string."""
        value, rest = decode_vlq("CAAA")
        assert value == 1
        assert rest == "AAA"

    def test_roundtrip(self):
        """Encoding then decoding returns original value."""
        for value in [0, 1, -1, 15, -15, 100, -100, 1000, -1000]:
            encoded = encode_vlq(value)
            decoded, rest = decode_vlq(encoded)
            assert decoded == value
            assert rest == ""


class TestSourceMapGenerator:
    """Test source map generation."""

    def test_empty_map(self):
        """Empty source map has correct structure."""
        gen = SourceMapGenerator(file="output.js")
        result = gen.generate()

        assert result["version"] == 3
        assert result["file"] == "output.js"
        assert result["sources"] == []
        assert result["mappings"] == ""

    def test_add_source(self):
        """Adding sources."""
        gen = SourceMapGenerator(file="output.js")
        idx = gen.add_source("input.py", "x = 1")

        assert idx == 0
        assert gen.sources == ["input.py"]
        assert gen.sources_content == ["x = 1"]

    def test_add_multiple_sources(self):
        """Adding multiple sources."""
        gen = SourceMapGenerator(file="output.js")
        idx1 = gen.add_source("a.py")
        idx2 = gen.add_source("b.py")

        assert idx1 == 0
        assert idx2 == 1
        assert gen.sources == ["a.py", "b.py"]

    def test_single_mapping(self):
        """Single mapping encodes correctly."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)

        result = gen.generate()
        # First segment: col=0, src=0, line=0, col=0 -> AAAA
        assert result["mappings"] == "AAAA"

    def test_multiple_mappings_same_line(self):
        """Multiple mappings on same generated line."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)
        gen.add_mapping(gen_line=0, gen_column=4, src_line=0, src_column=4)

        result = gen.generate()
        # Two segments on line 0, comma-separated
        assert "," in result["mappings"]
        assert ";" not in result["mappings"]

    def test_multiple_lines(self):
        """Mappings across multiple generated lines."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)
        gen.add_mapping(gen_line=1, gen_column=0, src_line=1, src_column=0)

        result = gen.generate()
        # Two lines, semicolon-separated
        assert ";" in result["mappings"]

    def test_empty_lines(self):
        """Empty generated lines produce empty segments."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)
        gen.add_mapping(gen_line=2, gen_column=0, src_line=2, src_column=0)

        result = gen.generate()
        # Line 0 has mapping, line 1 is empty, line 2 has mapping
        parts = result["mappings"].split(";")
        assert len(parts) == 3
        assert parts[0] != ""  # Line 0
        assert parts[1] == ""  # Line 1 (empty)
        assert parts[2] != ""  # Line 2

    def test_generate_json(self):
        """Generate valid JSON output."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py", "x = 1")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)

        json_str = gen.generate_json()
        parsed = json.loads(json_str)

        assert parsed["version"] == 3
        assert parsed["file"] == "output.js"
        assert parsed["sources"] == ["input.py"]

    def test_sources_content_included(self):
        """Source content is included when provided."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py", "x = 1\ny = 2")

        result = gen.generate()
        assert "sourcesContent" in result
        assert result["sourcesContent"] == ["x = 1\ny = 2"]

    def test_sources_content_not_included_when_none(self):
        """Source content is omitted when all None."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py", None)

        result = gen.generate()
        assert "sourcesContent" not in result

    def test_names_included(self):
        """Symbol names are included when provided."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(
            gen_line=0, gen_column=0, src_line=0, src_column=0, name="myVar"
        )

        result = gen.generate()
        assert "names" in result
        assert result["names"] == ["myVar"]

    def test_names_not_included_when_empty(self):
        """Names array is omitted when empty."""
        gen = SourceMapGenerator(file="output.js")
        gen.add_source("input.py")
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)

        result = gen.generate()
        assert "names" not in result


class TestSourceMapComment:
    """Test source map URL comment generation."""

    def test_basic_comment(self):
        """Basic sourceMappingURL comment."""
        comment = get_sourcemap_comment("output.js.map")
        assert comment == "//# sourceMappingURL=output.js.map\n"

    def test_comment_with_path(self):
        """Comment with path in filename."""
        comment = get_sourcemap_comment("./maps/output.js.map")
        assert comment == "//# sourceMappingURL=./maps/output.js.map\n"


class TestSourceMapIntegration:
    """Integration tests for source map generation."""

    def test_realistic_mapping(self):
        """Test a realistic source map scenario."""
        gen = SourceMapGenerator(file="example.js")
        source = """\
x = 1
y = 2
print(x + y)
"""
        gen.add_source("example.py", source)

        # Map: let x = 1;
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)
        gen.add_mapping(gen_line=0, gen_column=4, src_line=0, src_column=0, name="x")

        # Map: let y = 2;
        gen.add_mapping(gen_line=1, gen_column=0, src_line=1, src_column=0)
        gen.add_mapping(gen_line=1, gen_column=4, src_line=1, src_column=0, name="y")

        # Map: console.log(x + y);
        gen.add_mapping(gen_line=2, gen_column=0, src_line=2, src_column=0)

        result = gen.generate()

        assert result["version"] == 3
        assert result["sources"] == ["example.py"]
        assert result["names"] == ["x", "y"]
        assert ";" in result["mappings"]  # Multiple lines
        assert "," in result["mappings"]  # Multiple segments per line

    def test_column_tracking(self):
        """Test that column positions are correctly relative."""
        gen = SourceMapGenerator(file="test.js")
        gen.add_source("test.py")

        # Simulate: "const result = x + y;"
        #            ^0    ^6     ^15 ^17
        gen.add_mapping(gen_line=0, gen_column=0, src_line=0, src_column=0)
        gen.add_mapping(gen_line=0, gen_column=6, src_line=0, src_column=0, name="result")
        gen.add_mapping(gen_line=0, gen_column=15, src_line=0, src_column=9, name="x")
        gen.add_mapping(gen_line=0, gen_column=19, src_line=0, src_column=13, name="y")

        result = gen.generate()

        # Should have 4 comma-separated segments
        segments = result["mappings"].split(",")
        assert len(segments) == 4
