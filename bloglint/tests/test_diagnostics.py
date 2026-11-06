from __future__ import annotations

import unittest

from bloglint.diagnostics import (
    DiagnosticsConfig,
    analyze_body,
    analyze_document,
    summarize,
)
from bloglint.schema import Document
from bloglint.text import document_from_body


def categories(body: str, title: str = "") -> list[str]:
    return [issue.category for issue in analyze_body(body, title=title)]


class PhraseTests(unittest.TestCase):
    def test_filler_word_has_exact_span(self) -> None:
        body = "Thực sự thì việc viết rất khó."
        issues = analyze_body(body)
        filler = [issue for issue in issues if issue.category == "filler_word"]
        self.assertEqual(len(filler), 1)
        self.assertEqual(filler[0].span.text, "Thực sự")
        self.assertEqual(body[filler[0].span.start : filler[0].span.end], "Thực sự")

    def test_cliche_is_detected_once(self) -> None:
        body = "Trong thời đại ngày nay, ai cũng viết blog."
        issues = analyze_body(body)
        cliches = [issue for issue in issues if issue.category == "cliche"]
        self.assertEqual(len(cliches), 1)
        self.assertEqual(cliches[0].span.text, "Trong thời đại ngày nay")

    def test_clean_text_has_no_issues(self) -> None:
        body = "Bài viết này trình bày một ý tưởng nhỏ. Tác giả cố gắng giữ câu ngắn và rõ."
        self.assertEqual(analyze_body(body), [])


class SentenceAndParagraphTests(unittest.TestCase):
    def test_long_sentence(self) -> None:
        body = "từ " * 45
        issues = analyze_body(body)
        self.assertIn("sentence_too_long", [issue.category for issue in issues])

    def test_short_sentence_threshold_is_configurable(self) -> None:
        body = "một hai ba bốn năm sáu."
        config = DiagnosticsConfig(max_sentence_words=5)
        self.assertNotIn("sentence_too_long", categories(body))
        self.assertEqual(
            [issue.category for issue in analyze_body(body, config=config)],
            ["sentence_too_long"],
        )

    def test_long_paragraph(self) -> None:
        body = "một hai ba bốn năm sáu. " * 40
        config = DiagnosticsConfig(max_paragraph_words=20, max_sentence_words=100)
        issues = analyze_body(body, config=config)
        self.assertIn("paragraph_too_long", [issue.category for issue in issues])


class RepetitionTests(unittest.TestCase):
    def test_consecutive_repetition(self) -> None:
        body = "Đây là một ý tưởng rất rất hay."
        issues = analyze_body(body)
        repetition = [issue for issue in issues if issue.category == "repetition"]
        self.assertEqual(len(repetition), 1)
        self.assertEqual(repetition[0].span.text, "rất rất")

    def test_repeated_word_in_paragraph(self) -> None:
        body = "Ý tưởng hay. Ý tưởng mới. Ý tưởng rõ. Ý tưởng đẹp."
        issues = analyze_body(body)
        messages = [issue.message for issue in issues if issue.category == "repetition"]
        self.assertTrue(any("ý tưởng" in message or "tưởng" in message for message in messages))


class PunctuationTests(unittest.TestCase):
    def test_space_before_and_missing_space_after(self) -> None:
        body = "Câu này có lỗi , rồi sao?Được."
        issues = [issue for issue in analyze_body(body) if issue.category == "punctuation"]
        texts = sorted(issue.span.text for issue in issues)
        self.assertEqual(texts, sorted([" ,", "?"]))
        self.assertEqual(len(issues), 2)


class PassiveTests(unittest.TestCase):
    def test_passive_overuse(self) -> None:
        body = (
            "Tôi bị hỏi rất nhiều lần. Việc này bị lặp lại. Kết quả bị hiểu sai. "
            "Mọi người bị cuốn vào tranh luận. Nhưng cuối cùng thì câu chuyện vẫn "
            "được kể tiếp và mọi thứ dần rõ ràng hơn theo thời gian. "
            "Điều đó khiến người đọc khó theo dõi mạch văn và cảm thấy mệt mỏi."
        )
        issues = analyze_body(body)
        self.assertIn("passive_overuse", [issue.category for issue in issues])


class StructureAndMaskTests(unittest.TestCase):
    def test_structure_requires_headings_for_long_text(self) -> None:
        body = "từ " * 650
        self.assertIn("structure", categories(body))

    def test_long_text_with_heading_is_fine(self) -> None:
        body = "## Mục\n\n" + ("từ " * 650)
        self.assertNotIn("structure", categories(body))

    def test_code_block_is_ignored(self) -> None:
        body = "```\nthực sự , lỗi\n```\n"
        self.assertEqual(analyze_body(body), [])

    def test_inline_code_and_url_are_ignored(self) -> None:
        body = "Dùng `thực sự` và https://example.com/a,b để thử."
        self.assertEqual(analyze_body(body), [])


class DeterminismTests(unittest.TestCase):
    def test_same_input_same_output(self) -> None:
        body = "Thực sự thì đây là câu rất dài , có lỗi.Đoạn này lặp lặp."
        first = [issue.to_dict() for issue in analyze_body(body)]
        second = [issue.to_dict() for issue in analyze_body(body)]
        self.assertEqual(first, second)

    def test_document_api_matches_body_api(self) -> None:
        body = "Thực sự thì đây là một câu."
        document = document_from_body(body, title="T")
        self.assertEqual(
            [issue.to_dict() for issue in analyze_document(document)],
            [issue.to_dict() for issue in analyze_body(body, title="T")],
        )


class SummaryTests(unittest.TestCase):
    def test_summary_counts(self) -> None:
        issues = analyze_body("Thực sự thì đây là câu rất dài , có lỗi.")
        summary = summarize(issues)
        self.assertEqual(summary["total"], len(issues))
        self.assertEqual(sum(summary["by_severity"].values()), len(issues))
        self.assertEqual(sum(summary["by_category"].values()), len(issues))


class DocumentInputTests(unittest.TestCase):
    def test_accepts_document_object(self) -> None:
        document = Document(path="x.md", title="X", body="Nội dung sạch.")
        self.assertEqual(analyze_document(document), [])


if __name__ == "__main__":
    unittest.main()
