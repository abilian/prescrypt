"""Source map generation for Python-to-JavaScript transpilation.

Implements Source Map Version 3 specification.
https://sourcemaps.info/spec.html
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Base64 VLQ encoding alphabet
VLQ_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
VLQ_SHIFT = 5
VLQ_CONTINUATION_BIT = 1 << VLQ_SHIFT
VLQ_MASK = VLQ_CONTINUATION_BIT - 1


def encode_vlq(value: int) -> str:
    """Encode a single integer as a VLQ (Variable Length Quantity).

    VLQ uses base64 encoding where:
    - The sign bit is stored in the least significant bit
    - Continuation bits indicate more digits follow
    """
    # Convert to unsigned with sign in LSB
    if value < 0:
        value = ((-value) << 1) | 1
    else:
        value = value << 1

    result = []
    while True:
        digit = value & VLQ_MASK
        value >>= VLQ_SHIFT
        if value > 0:
            digit |= VLQ_CONTINUATION_BIT
        result.append(VLQ_CHARS[digit])
        if value == 0:
            break

    return "".join(result)


def decode_vlq(encoded: str) -> tuple[int, str]:
    """Decode a VLQ value from a string, returning (value, remaining_string)."""
    result = 0
    shift = 0

    for i, char in enumerate(encoded):
        digit = VLQ_CHARS.index(char)
        result |= (digit & VLQ_MASK) << shift
        shift += VLQ_SHIFT

        if not (digit & VLQ_CONTINUATION_BIT):
            # Check sign bit (LSB)
            if result & 1:
                result = -(result >> 1)
            else:
                result = result >> 1
            return result, encoded[i + 1 :]

    msg = "Invalid VLQ: unexpected end of string"
    raise ValueError(msg)


@dataclass
class Mapping:
    """A single source mapping entry.

    Maps a position in generated code to a position in source code.
    """

    # Position in generated JavaScript (0-indexed)
    gen_line: int
    gen_column: int

    # Position in source Python (0-indexed)
    src_line: int
    src_column: int

    # Source file index (for multi-source maps)
    src_index: int = 0

    # Optional: name index for symbol mappings
    name_index: int | None = None


@dataclass
class SourceMapGenerator:
    """Generates Source Map Version 3 JSON.

    Usage:
        gen = SourceMapGenerator("output.js")
        gen.add_source("input.py", source_content)
        gen.add_mapping(gen_line=0, gen_col=0, src_line=0, src_col=0)
        gen.add_mapping(gen_line=1, gen_col=4, src_line=2, src_col=0)
        source_map = gen.generate()
    """

    # Output filename (the .js file)
    file: str

    # Source files
    sources: list[str] = field(default_factory=list)
    sources_content: list[str | None] = field(default_factory=list)

    # Symbol names (for minification - typically empty for us)
    names: list[str] = field(default_factory=list)

    # Mappings
    mappings: list[Mapping] = field(default_factory=list)

    def add_source(self, filename: str, content: str | None = None) -> int:
        """Add a source file and return its index."""
        index = len(self.sources)
        self.sources.append(filename)
        self.sources_content.append(content)
        return index

    def add_mapping(
        self,
        gen_line: int,
        gen_column: int,
        src_line: int,
        src_column: int,
        src_index: int = 0,
        name: str | None = None,
    ) -> None:
        """Add a mapping from generated position to source position.

        All positions are 0-indexed.
        """
        name_index = None
        if name is not None:
            if name not in self.names:
                self.names.append(name)
            name_index = self.names.index(name)

        self.mappings.append(
            Mapping(
                gen_line=gen_line,
                gen_column=gen_column,
                src_line=src_line,
                src_column=src_column,
                src_index=src_index,
                name_index=name_index,
            )
        )

    def _encode_mappings(self) -> str:
        """Encode all mappings as a VLQ string.

        Format: semicolon-separated lines, comma-separated segments.
        Each segment is 4-5 VLQ values:
          - generated column (relative)
          - source index (relative)
          - source line (relative)
          - source column (relative)
          - name index (optional, relative)
        """
        if not self.mappings:
            return ""

        # Sort mappings by generated position
        sorted_mappings = sorted(
            self.mappings, key=lambda m: (m.gen_line, m.gen_column)
        )

        # Group by generated line
        lines: list[list[Mapping]] = []
        current_line = 0

        for mapping in sorted_mappings:
            # Add empty lines if needed
            while len(lines) <= mapping.gen_line:
                lines.append([])
            lines[mapping.gen_line].append(mapping)

        # Encode each line
        result = []

        # Track previous values for relative encoding
        prev_gen_col = 0
        prev_src_index = 0
        prev_src_line = 0
        prev_src_col = 0
        prev_name_index = 0

        for line_mappings in lines:
            line_segments = []
            prev_gen_col = 0  # Reset column for each line

            for mapping in line_mappings:
                segment = []

                # Generated column (relative to previous in this line)
                segment.append(encode_vlq(mapping.gen_column - prev_gen_col))
                prev_gen_col = mapping.gen_column

                # Source index (relative)
                segment.append(encode_vlq(mapping.src_index - prev_src_index))
                prev_src_index = mapping.src_index

                # Source line (relative)
                segment.append(encode_vlq(mapping.src_line - prev_src_line))
                prev_src_line = mapping.src_line

                # Source column (relative)
                segment.append(encode_vlq(mapping.src_column - prev_src_col))
                prev_src_col = mapping.src_column

                # Name index (optional, relative)
                if mapping.name_index is not None:
                    segment.append(encode_vlq(mapping.name_index - prev_name_index))
                    prev_name_index = mapping.name_index

                line_segments.append("".join(segment))

            result.append(",".join(line_segments))

        return ";".join(result)

    def generate(self) -> dict:
        """Generate the source map as a dictionary."""
        source_map = {
            "version": 3,
            "file": self.file,
            "sources": self.sources,
            "mappings": self._encode_mappings(),
        }

        # Only include sourcesContent if we have any
        if any(c is not None for c in self.sources_content):
            source_map["sourcesContent"] = self.sources_content

        # Only include names if we have any
        if self.names:
            source_map["names"] = self.names

        return source_map

    def generate_json(self, indent: int | None = None) -> str:
        """Generate the source map as a JSON string."""
        return json.dumps(self.generate(), indent=indent)

    def write(self, path: Path) -> None:
        """Write the source map to a file."""
        path.write_text(self.generate_json())


def get_sourcemap_comment(map_filename: str) -> str:
    """Get the sourceMappingURL comment to append to generated JS."""
    return f"//# sourceMappingURL={map_filename}\n"
