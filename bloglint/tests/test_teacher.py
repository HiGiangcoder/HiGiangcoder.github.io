from __future__ import annotations

import json
import unittest

from bloglint.teacher import (
    NetworkNotAllowed,
    OllamaTeacher,
    TeacherResponseError,
    build_prompt,
    extract_json,
    issues_from_payload,
)
from bloglint.text import document_from_body

BODY = "Trong thời đại ngày nay, ai cũng muốn viết nhanh. Thực sự thì viết chậm lại giúp nghĩ sâu."


def teacher(transport=None, **kwargs) -> OllamaTeacher:
    return OllamaTeacher(
        model="gpt-oss:120b-cloud",
        base_url="http://localhost:11434",
        transport=transport,
        **kwargs,
    )


class PromptTests(unittest.TestCase):
    def test_prompt_contains_body_and_format(self) -> None:
        document = document_from_body(BODY, title="Thử")
        prompt = build_prompt(document)
        self.assertIn("Thử", prompt)
        self.assertIn(BODY, prompt)
        self.assertIn('"issues"', prompt)
        self.assertIn("quote", prompt)

    def test_prompt_includes_guide_context_when_provided(self) -> None:
        document = document_from_body(BODY, title="Thử")
        prompt = build_prompt(document, guide_context="TÀI LIỆU: viết câu ngắn.")
        self.assertIn("TÀI LIỆU THAM KHẢO (RAG)", prompt)
        self.assertIn("TÀI LIỆU: viết câu ngắn.", prompt)

    def test_prompt_omits_guide_section_when_empty(self) -> None:
        document = document_from_body(BODY)
        prompt = build_prompt(document, guide_context="   ")
        self.assertNotIn("TÀI LIỆU THAM KHẢO (RAG)", prompt)


class GuardTests(unittest.TestCase):
    def test_network_is_denied_by_default(self) -> None:
        document = document_from_body(BODY)
        with self.assertRaises(NetworkNotAllowed):
            teacher().annotate(document)

    def test_explicit_false_overrides_instance_flag(self) -> None:
        document = document_from_body(BODY)
        instance = teacher(allow_network=True)
        with self.assertRaises(NetworkNotAllowed):
            instance.annotate(document, allow_network=False)


class ParsingTests(unittest.TestCase):
    def test_extract_json_from_fence(self) -> None:
        payload = extract_json('```json\n{"issues": []}\n```')
        self.assertEqual(payload, {"issues": []})

    def test_extract_json_from_surrounding_text(self) -> None:
        payload = extract_json('Đây là kết quả: {"issues": []} hết.')
        self.assertEqual(payload, {"issues": []})

    def test_extract_json_accepts_list(self) -> None:
        payload = extract_json('[{"category": "clarity"}]')
        self.assertEqual(payload, {"issues": [{"category": "clarity"}]})

    def test_invalid_json_rejected(self) -> None:
        with self.assertRaises(TeacherResponseError):
            extract_json("không có json")

    def test_empty_response_rejected(self) -> None:
        with self.assertRaises(TeacherResponseError):
            extract_json("   ")

    def test_quote_is_mapped_to_span(self) -> None:
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "warning",
                    "message": "Câu mở đầu sáo ngữ",
                    "suggestion": "Viết cụ thể hơn",
                    "quote": "Trong thời đại ngày nay",
                }
            ]
        }
        issues = issues_from_payload(payload, BODY)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].span.text, "Trong thời đại ngày nay")
        self.assertEqual(issues[0].source, "teacher")

    def test_quote_with_normalized_whitespace_maps_back(self) -> None:
        body = "Thực sự thì việc bắt\nđầu không khó."
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "info",
                    "message": "Câu mở đầu",
                    "quote": "Thực sự thì việc bắt đầu không khó.",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        self.assertEqual(issues[0].span.start, 0)
        self.assertEqual(issues[0].span.end, len(body))
        self.assertEqual(issues[0].span.text, body)

    def test_quote_with_extra_spaces_maps_back(self) -> None:
        body = "Một  câu   có khoảng trắng."
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "info",
                    "message": "x",
                    "quote": "Một câu có khoảng trắng.",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        self.assertEqual(issues[0].span.start, 0)
        self.assertEqual(issues[0].span.end, len(body))

    def test_quote_ignores_case_and_markdown_bold(self) -> None:
        body = "Thứ hai, khán giả bị **xẹp lại thành một**. Trên mạng ai cũng thấy."
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "info",
                    "message": "x",
                    "quote": "Khán giả bị **xẹp lại thành một**.",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        span_text = issues[0].span.text
        self.assertIn("khán giả bị **xẹp lại thành một", span_text)
        self.assertEqual(body[issues[0].span.start : issues[0].span.end], span_text)

    def test_quote_ignores_punctuation_difference(self) -> None:
        body = "Họ hỏi: “làm sao để những quy tắc ấy có thể bị chất vấn?”"
        payload = {
            "issues": [
                {
                    "category": "clarity",
                    "severity": "info",
                    "message": "x",
                    "quote": "làm sao để những quy tắc ấy có thể bị chất vấn!",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        self.assertIn("chất vấn", issues[0].span.text)

    def test_quote_with_curly_quotes_and_blank_line(self) -> None:
        body = 'Sẵn sàng chưa?\n\n"Tiêu."\n\nBắt đầu!\n'
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "info",
                    "message": "x",
                    "quote": "“Tiêu.”\nBắt đầu!",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        self.assertIn("Tiêu", issues[0].span.text)
        self.assertIn("Bắt đầu", issues[0].span.text)

    def test_quote_with_one_word_paraphrase_maps_to_common_span(self) -> None:
        body = (
            "Chúng ta phải xác định mục tiêu nhằm nhìn thấy vị trí của bản thân, "
            "rằng ta đã tiến bộ đến nhường nào rồi."
        )
        payload = {
            "issues": [
                {
                    "category": "clarity",
                    "severity": "info",
                    "message": "x",
                    "quote": "để nhìn thấy vị trí của bản thân, rằng ta đã tiến bộ đến nhường nào rồi.",
                }
            ]
        }
        issues = issues_from_payload(payload, body)
        self.assertTrue(issues[0].span.text.startswith("nhìn thấy vị trí"))
        self.assertIn("nhường nào rồi", issues[0].span.text)

    def test_missing_quote_is_rejected(self) -> None:
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "warning",
                    "message": "x",
                    "quote": "không có trong bài",
                }
            ]
        }
        with self.assertRaises(TeacherResponseError):
            issues_from_payload(payload, BODY)

    def test_invalid_category_maps_to_other(self) -> None:
        payload = {
            "issues": [
                {
                    "category": "không_tồn_tại",
                    "severity": "warning",
                    "message": "x",
                    "quote": "Thực sự",
                }
            ]
        }
        issues = issues_from_payload(payload, BODY)
        self.assertEqual(issues[0].category, "other")

    def test_invalid_severity_maps_to_warning(self) -> None:
        payload = {
            "issues": [
                {
                    "category": "style",
                    "severity": "fatal",
                    "message": "x",
                    "quote": "Thực sự",
                }
            ]
        }
        issues = issues_from_payload(payload, BODY)
        self.assertEqual(issues[0].severity, "warning")


class TransportTests(unittest.TestCase):
    def test_annotate_with_fake_transport(self) -> None:
        captured = {}

        def transport(url, payload, headers):
            captured["url"] = url
            captured["payload"] = payload
            captured["headers"] = headers
            return {
                "message": {
                    "content": json.dumps(
                        {
                            "issues": [
                                {
                                    "category": "clarity",
                                    "severity": "info",
                                    "message": "Câu mở đầu chung chung",
                                    "suggestion": "Nêu vấn đề cụ thể",
                                    "quote": "Thực sự",
                                }
                            ]
                        },
                        ensure_ascii=False,
                    )
                },
                "done": True,
            }

        document = document_from_body(BODY, title="Thử")
        result = teacher(transport=transport).annotate(document, allow_network=True)

        self.assertEqual(captured["url"], "http://localhost:11434/api/chat")
        self.assertEqual(captured["payload"]["model"], "gpt-oss:120b-cloud")
        self.assertFalse(captured["payload"]["stream"])
        self.assertEqual(captured["payload"]["format"], "json")
        self.assertEqual(captured["headers"], {})
        self.assertEqual(len(result.issues), 1)
        self.assertTrue(result.meta["done"])

    def test_api_key_sent_but_not_exposed(self) -> None:
        captured = {}

        def transport(url, payload, headers):
            captured["headers"] = headers
            return {"message": {"content": '{"issues": []}'}, "done": True}

        instance = OllamaTeacher(
            model="gpt-oss:120b-cloud",
            base_url="https://ollama.com",
            api_key="secret-value",
            transport=transport,
        )
        result = instance.annotate(document_from_body(BODY), allow_network=True)
        self.assertEqual(captured["headers"]["Authorization"], "Bearer secret-value")
        self.assertNotIn("secret-value", json.dumps(result.meta, ensure_ascii=False))
        self.assertNotIn("secret-value", result.raw)

    def test_http_error_shape_is_rejected(self) -> None:
        def transport(url, payload, headers):
            return {"error": "boom"}

        with self.assertRaises(TeacherResponseError):
            teacher(transport=transport).annotate(
                document_from_body(BODY), allow_network=True
            )


if __name__ == "__main__":
    unittest.main()
