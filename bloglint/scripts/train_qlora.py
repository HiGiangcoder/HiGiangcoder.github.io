#!/usr/bin/env python3
"""Train BlogLint Student bằng QLoRA.

Script này **không chạy tự động**. Nó chỉ thực hiện training khi có cả:

- ``--allow-train``: người dùng đã duyệt train;
- ``--allow-download``: cho phép tải model/checkpoint từ Hugging Face.

Mặc định script chạy ở chế độ dry-run, kiểm tra config và dữ liệu, không import
thư viện nặng.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "model_id": "Qwen/Qwen3-VL-2B-Instruct",
    "train_file": "data/sft-v4/train.jsonl",
    "val_file": "data/sft-v4/val.jsonl",
    "output_dir": "data/train-runs/pilot-001",
    "max_seq_length": 6144,
    "num_train_epochs": 3.0,
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "learning_rate": 0.0002,
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "optim": "paged_adamw_8bit",
    "bf16": True,
    "gradient_checkpointing": True,
    "eval_steps": 20,
    "save_steps": 50,
    "logging_steps": 5,
    "seed": 42,
    "target_modules": "all-linear",
}


def load_config(path: Path | None) -> dict:
    config = dict(DEFAULT_CONFIG)
    if path is not None:
        with path.open("r", encoding="utf-8") as handle:
            user_config = json.load(handle)
        config.update(user_config)
    return config


def validate_data(config: dict) -> dict:
    train_path = Path(config["train_file"])
    val_path = Path(config["val_file"])
    if not train_path.exists():
        raise FileNotFoundError(f"Không tìm thấy train file: {train_path}")
    if not val_path.exists():
        raise FileNotFoundError(f"Không tìm thấy val file: {val_path}")

    def read_rows(path: Path) -> list[dict]:
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: JSON không hợp lệ: {exc}") from exc
                if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
                    raise ValueError(f"{path}:{line_number}: thiếu messages.")
                rows.append(payload)
        return rows

    train_rows = read_rows(train_path)
    val_rows = read_rows(val_path)
    if not train_rows:
        raise ValueError("Train rỗng.")
    if not val_rows:
        raise ValueError("Validation rỗng.")
    max_user = max(len(row["messages"][0].get("content", "")) for row in train_rows)
    return {
        "train_examples": len(train_rows),
        "val_examples": len(val_rows),
        "max_user_chars": max_user,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train BlogLint Student bằng QLoRA")
    parser.add_argument("--config", default=None, help="File JSON config.")
    parser.add_argument("--allow-train", action="store_true", help="Cho phép train thật.")
    parser.add_argument(
        "--allow-download", action="store_true", help="Cho phép tải model từ Hugging Face."
    )
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra config/dữ liệu.")
    parser.add_argument("--max-steps", type=int, default=None, help="Giới hạn số step để smoke test.")
    parser.add_argument("--gpu", default=None, help="CUDA_VISIBLE_DEVICES, ví dụ 0 hoặc 1.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config).expanduser() if args.config else None)
    stats = validate_data(config)
    print("Config hợp lệ.")
    print(f"- model: {config['model_id']}")
    print(f"- train: {config['train_file']} ({stats['train_examples']} example)")
    print(f"- val: {config['val_file']} ({stats['val_examples']} example)")
    print(f"- max user chars: {stats['max_user_chars']}")
    print(f"- output: {config['output_dir']}")
    print(f"- max_seq_length: {config['max_seq_length']}")

    if args.dry_run or not args.allow_train:
        if not args.allow_train:
            print("\nChưa có --allow-train: dừng sau kiểm tra. Không train.")
        return 0

    if args.gpu is not None:
        import os

        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    if not args.allow_download:
        import os

        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    # Import nặng chỉ xảy ra khi thực sự train.
    import torch
    from datasets import load_dataset
    from peft import LoraConfig
    from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    if not torch.cuda.is_available():
        raise RuntimeError("Không có CUDA. Training QLoRA cần GPU.")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForImageTextToText.from_pretrained(
        config["model_id"],
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    processor = AutoProcessor.from_pretrained(
        config["model_id"], trust_remote_code=True
    )

    peft_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=config["target_modules"],
    )

    dataset = load_dataset(
        "json",
        data_files={
            "train": config["train_file"],
            "validation": config["val_file"],
        },
    )

    sft_args = SFTConfig(
        output_dir=config["output_dir"],
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        learning_rate=config["learning_rate"],
        optim=config["optim"],
        bf16=config["bf16"],
        gradient_checkpointing=config["gradient_checkpointing"],
        eval_strategy="steps",
        eval_steps=config["eval_steps"],
        save_strategy="steps",
        save_steps=config["save_steps"],
        logging_steps=config["logging_steps"],
        max_length=config["max_seq_length"],
        assistant_only_loss=True,
        packing=False,
        seed=config["seed"],
        report_to="none",
        remove_unused_columns=False,
    )
    if args.max_steps is not None:
        sft_args.max_steps = args.max_steps

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        processing_class=processor,
        peft_config=peft_config,
        quantization_config=bnb_config,
    )

    trainer.train()
    trainer.save_model(config["output_dir"])
    processor.save_pretrained(config["output_dir"])
    with Path(config["output_dir"], "training_config.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"\nĐã lưu adapter tại: {config['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
