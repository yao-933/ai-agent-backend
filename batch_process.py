#!/usr/bin/env python3
"""
批量处理脚本 — 从 input.csv 读取 prompts，调用 Agent 后将结果写入 output.csv。

用法:
    python batch_process.py                           # 默认读取 input.csv → output.csv
    python batch_process.py --input prompts.csv       # 指定输入文件
    python batch_process.py --output results.csv      # 指定输出文件
    python batch_process.py --mode http               # 通过 HTTP API 调用（需先启动服务）

CSV 格式要求:
    输入文件至少包含一列 `prompt`（标题行必须存在）。
    输出文件包含 `prompt` 和 `answer` 两列。
"""

import csv
import asyncio
import sys
import time
from pathlib import Path

# 确保可以导入 app 包
sys.path.insert(0, str(Path(__file__).resolve().parent))


async def process_batch_direct(input_file: str, output_file: str) -> None:
    """直接导入 Agent 处理（更快，推荐）。"""
    from app.agent import run_agent

    prompts = _read_prompts(input_file)
    print(f"📄 读取到 {len(prompts)} 条 prompt，开始处理...\n")

    results: list[dict[str, str]] = []
    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] 🧠 {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
        start = time.perf_counter()
        try:
            answer = await run_agent(prompt)
        except Exception as e:
            answer = f"❌ 错误：{e}"
        elapsed = time.perf_counter() - start
        print(f"     ⏱ {elapsed:.1f}s → {answer[:80]}{'...' if len(answer) > 80 else ''}\n")
        results.append({"prompt": prompt, "answer": answer})

    _write_results(output_file, results)
    print(f"✅ 完成！结果已写入 {output_file}")


async def process_batch_http(input_file: str, output_file: str, base_url: str = "http://localhost:8000") -> None:
    """通过 HTTP API 调用 Agent（需要先启动服务）。"""
    import httpx

    prompts = _read_prompts(input_file)
    print(f"📄 读取到 {len(prompts)} 条 prompt，通过 HTTP 调用 {base_url}/chat ...\n")

    results: list[dict[str, str]] = []
    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
        for i, prompt in enumerate(prompts, 1):
            print(f"[{i}/{len(prompts)}] 🧠 {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
            start = time.perf_counter()
            try:
                resp = await client.post(f"{base_url}/chat", json={"prompt": prompt})
                resp.raise_for_status()
                answer = resp.json()["answer"]
            except Exception as e:
                answer = f"❌ HTTP 错误：{e}"
            elapsed = time.perf_counter() - start
            print(f"     ⏱ {elapsed:.1f}s → {answer[:80]}{'...' if len(answer) > 80 else ''}\n")
            results.append({"prompt": prompt, "answer": answer})

    _write_results(output_file, results)
    print(f"✅ 完成！结果已写入 {output_file}")


# ── 辅助函数 ──────────────────────────────────────────────────

def _read_prompts(path: str) -> list[str]:
    """从 CSV 读取 prompt 列。"""
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "prompt" not in (reader.fieldnames or []):
            raise SystemExit(f"❌ CSV 文件缺少 'prompt' 列，当前列名：{reader.fieldnames}")
        return [row["prompt"].strip() for row in reader if row.get("prompt", "").strip()]


def _write_results(path: str, rows: list[dict[str, str]]) -> None:
    """将结果写入 CSV。"""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["prompt", "answer"])
        writer.writeheader()
        writer.writerows(rows)


# ── CLI 入口 ──────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="批量处理 CSV 中的 prompts，调用 AI Agent 生成回答",
    )
    parser.add_argument("--input",  default="input.csv",  help="输入 CSV 文件路径（默认 input.csv）")
    parser.add_argument("--output", default="output.csv", help="输出 CSV 文件路径（默认 output.csv）")
    parser.add_argument("--mode",   default="direct", choices=["direct", "http"],
                        help="运行模式：direct=直接导入Agent(默认), http=通过HTTP API调用")
    parser.add_argument("--url",    default="http://localhost:8000",
                        help="HTTP 模式下的 API 地址（默认 http://localhost:8000）")
    args = parser.parse_args()

    if args.mode == "http":
        asyncio.run(process_batch_http(args.input, args.output, args.url))
    else:
        asyncio.run(process_batch_direct(args.input, args.output))
