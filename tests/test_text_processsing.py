from app.services.text_processing_service import (
    clean_extracted_text,
    split_into_chunks,
)


def test_clean_extracted_text() -> None:
    raw_text = """
        Hello     world.


        This   is   a test.
    """

    cleaned = clean_extracted_text(raw_text)

    assert cleaned == "Hello world.\n\nThis is a test."


def test_cleaned_text_removes_control_characters() -> None:
    raw_text = "Hello\x00 world"

    cleaned = clean_extracted_text(raw_text)

    assert "\x00" not in cleaned
    assert "Hello" in cleaned
    assert "world" in cleaned


def test_split_into_chunks() -> None:
    text = (
        "Paragraph one contains some information.\n\n"
        "Paragraph two contains more information.\n\n"
        "Paragraph three contains additional information."
    )

    chunks = split_into_chunks(
        text,
        max_characters=60,
        overlap=10,
    )

    assert len(chunks) >= 2

    for index, chunk in enumerate(chunks):
        assert chunk.index == index
        assert chunk.text
        assert chunk.character_count == len(chunk.text)


def test_empty_text_returns_no_chunks() -> None:
    chunks = split_into_chunks("")

    assert chunks == []
