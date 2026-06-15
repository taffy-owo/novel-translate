import re

paragraph_separator_pattern = re.compile(r"(?:\r?\n\s*){2,}")


def split_into_segments(text: str) -> list[str]:
    # Contract: blank-line separated paragraphs are translation segments; surrounding
    # whitespace is not part of the segment, and empty paragraphs are ignored.
    return [
        segment_text
        for raw_segment in paragraph_separator_pattern.split(text)
        if (segment_text := raw_segment.strip())
    ]
