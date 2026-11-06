#!/usr/bin/env python3
"""Sinh predictions của Student từ adapter đã train.

Script chỉ chạy khi có --allow-inference. Mặc định dry-run kiểm tra dữ liệu.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_ADAPTER = "data/train-runs/pilot-001"


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sinh predictions của Student")
    parser.add_argument("--adapter", default=DEFAULT_ADAPTER)
    parser.add_argument("--input", required=True, help="JSONL chứa messages (train/val/test).")
    parser.add_argument("--output", required=True, help="JSONL predictions.")
    parser.add_argument("--allow-inference", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--gpu", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser()
    rows = load_rows(input_path)
    print(f"Input: {input_path} ({len(rows)} example)")
    print(f"Adapter: {args.adapter}")
    print(f"Output: {output_path}")

    if args.dry_run or not args.allow_inference:
        if not args.allow_inference:
            print("Chưa có --allow-inference: dừng sau kiểm tra.")
        return 0

    if args.gpu is not None:
        import os

        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    import torch
    from peft import PeftModel
    from transformers import AutoModelForImageTextToText, AutoProcessor

    adapter_path = Path(args.adapter)
    base_model_id = None
    config_path = adapter_path / "training_config.json"
    if config_path.exists():
        base_model_id = json.loads(config_path.read_text(encoding="utf-8")).get("model_id")
    if not base_model_id:
        base_model_id = "Qwen/Qwen3-VL-2B-Instruct"

    processor = AutoProcessor.from_pretrained(base_model_id, trust_remote_code=True)
    base_model = AutoModelForImageTextToText.from_pretrained(
        base_model_id, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    )
    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    model.eval()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(rows, start=1):
            prompt = row["messages"][0]["content"]
            meta = row.get("meta", {})
            if hasattr(processor, "apply_chat_template"):
                prompt = processor.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    tokenize=False,
                    add_generation_prompt=True,
                )
            inputs = processor(text=[prompt], return_tensors="pt")
            inputs = {key: value.to(model.device) for key, value in inputs.items()}
            import torch
            from transformers import StoppingCriteria, StoppingCriteriaList

            class JsonComplete(StoppingCriteria):
                def __init__(self, processor, prompt_length):
                    self.processor = processor
                    self.prompt_length = prompt_length

                def __call__(self, input_ids, scores, **kwargs):
                    generated = input_ids[0][self.prompt_length:]
                    text = self.processor.decode(generated, skip_special_tokens=True)
                    try:
                        json.loads(text)
                        return True
                    except Exception:
                        return False

            stopping = StoppingCriteriaList([JsonComplete(processor, inputs["input_ids"].shape[1])])
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    stopping_criteria=stopping,
                )
            new_tokens = generated[0][inputs["input_ids"].shape[1] :]
            raw = processor.decode(new_tokens, skip_special_tokens=True)
            try:
                payload = json.loads(raw)
                issues = payload.get("issues", [])
                if not isinstance(issues, list):
                    issues = []
                    parse_ok = False
                else:
                    parse_ok = True
            except json.JSONDecodeError:
                issues = []
                parse_ok = False
            record = {
                "content_sha256": meta.get("content_sha256"),
                "source_path": meta.get("source_path"),
                "issues": issues,
                "raw": raw,
                "parse_ok": parse_ok,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            written += 1
            print(f"[{index}/{len(rows)}] parse_ok={parse_ok} issues={len(issues)}")
    print(f"Đã ghi {written} prediction vào {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
