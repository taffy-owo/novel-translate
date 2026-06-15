from novel_translate.modules.ingest.segment import split_into_segments


def test_split_into_segments_uses_blank_lines() -> None:
    text = " first paragraph \n\nsecond paragraph\r\n\r\n third paragraph "

    segments = split_into_segments(text)

    assert segments == ["first paragraph", "second paragraph", "third paragraph"]


def test_split_into_segments_discards_empty_paragraphs() -> None:
    text = "\n\n first \n\n\n   \n\n second \n\n"

    segments = split_into_segments(text)

    assert segments == ["first", "second"]


def test_split_into_segments_keeps_single_segment() -> None:
    text = "only one paragraph\nwith an internal line"

    segments = split_into_segments(text)

    assert segments == ["only one paragraph\nwith an internal line"]
