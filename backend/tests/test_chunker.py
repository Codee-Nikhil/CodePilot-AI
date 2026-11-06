from app.ai.chunker import chunk_text


def test_empty_or_blank_text_has_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("\n\n  \n") == []


def test_small_file_is_one_chunk():
    chunks = chunk_text("a\nb\nc")
    assert len(chunks) == 1
    assert (chunks[0].start_line, chunks[0].end_line) == (1, 3)


def test_large_file_is_split_with_overlap_and_no_gaps():
    chunks = chunk_text("\n".join("x" * 50 for _ in range(200)))
    assert len(chunks) > 5
    assert chunks[0].start_line == 1 and chunks[-1].end_line == 200
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev.start_line < nxt.start_line <= prev.end_line + 1
    assert all(len(c.text) <= 1200 for c in chunks)


def test_very_long_line_is_split():
    chunks = chunk_text("y" * 5000)
    assert len(chunks) == 5 and all(len(c.text) <= 1200 for c in chunks)
