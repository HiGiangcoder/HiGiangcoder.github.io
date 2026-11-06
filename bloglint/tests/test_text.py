from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from bloglint.text import (
    count_words,
    load_document,
    mask_code,
    split_front_matter,
    split_paragraphs,
    split_sentences,
)


class FrontMatterTests(unittest.TestCase):
    def test_split_and_offset(self) -> None:
        text = "---\ntitle: Xin chào\ntags: [a]\n---\nNội dung bài."
        metadata, body, offset = split_front_matter(text)
        self.assertEqual(metadata["title"], "Xin chào")
        self.assertEqual(body, "Nội dung bài.")
        self.assertEqual(text[offset:], body)

    def test_without_front_matter(self) -> None:
        metadata, body, offset = split_front_matter("Chỉ là nội dung.")
        self.assertEqual(metadata, {})
        self.assertEqual(body, "Chỉ là nội dung.")
        self.assertEqual(offset, 0)

    def test_invalid_yaml_rejected(self) -> None:
        with self.assertRaises(Exception):
            split_front_matter("---\ntitle: [\n---\nbody")


class ParagraphTests(unittest.TestCase):
    def test_offsets(self) -> None:
        body = "Đoạn một.\n\nĐoạn hai.\n"
        paragraphs = split_paragraphs(body)
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0].text, "Đoạn một.")
        self.assertEqual(paragraphs[1].start, body.index("Đoạn hai"))
        self.assertEqual(body[paragraphs[1].start : paragraphs[1].end], "Đoạn hai.")

    def test_leading_whitespace_is_excluded(self) -> None:
        body = "   Đoạn có thụt lề.\n"
        paragraph = split_paragraphs(body)[0]
        self.assertEqual(paragraph.text, "Đoạn có thụt lề.")
        self.assertEqual(paragraph.start, 3)


class SentenceTests(unittest.TestCase):
    def test_offsets_are_absolute(self) -> None:
        text = "Câu một. Câu hai! Còn ba?"
        sentences = split_sentences(text, absolute_start=100, paragraph_index=0)
        self.assertEqual([s.text for s in sentences], ["Câu một.", "Câu hai!", "Còn ba?"])
        self.assertEqual(sentences[0].start, 100)
        self.assertEqual(sentences[1].start, 100 + text.index("Câu hai"))
        self.assertTrue(all(s.paragraph_index == 0 for s in sentences))

    def test_trailing_text_without_punctuation(self) -> None:
        sentences = split_sentences("Một câu", absolute_start=0, paragraph_index=2)
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0].text, "Một câu")


class MaskTests(unittest.TestCase):
    def test_length_is_preserved(self) -> None:
        text = "Trước `code` sau.\n\n```py\nx = 1\n```\nhttps://example.com"
        masked = mask_code(text)
        self.assertEqual(len(masked), len(text))

    def test_code_content_is_blanked(self) -> None:
        masked = mask_code("A `thực sự` B")
        self.assertNotIn("thực sự", masked)
        self.assertIn("A", masked)


class LoadDocumentTests(unittest.TestCase):
    def test_title_from_front_matter(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "sample_post.md"
        document = load_document(fixture)
        self.assertEqual(document.title, "Một bài mẫu để kiểm tra BlogLint")
        self.assertTrue(document.paragraphs)
        self.assertNotIn("---", document.body)

    def test_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bai.md"
            path.write_text("---\ntitle: T\n---\nNội dung.", encoding="utf-8")
            document = load_document(path)
            self.assertEqual(document.title, "T")
            self.assertEqual(document.body, "Nội dung.")

    def test_count_words(self) -> None:
        self.assertEqual(count_words("một hai ba"), 3)


if __name__ == "__main__":
    unittest.main()
