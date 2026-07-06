import re
import sys
import time
import pathlib
from openai import OpenAI

from .srt_utils import parse_srt, compose_srt, merge_short_entries

PROMPT_PATH = pathlib.Path(__file__).parent / "final_prompt.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8").strip()


def build_batch_text(entries):
    body = "\n\n".join(f"#{i}\nOriginal>\n{t}" for i, _, t in entries)
    return f"<entries>\n{body}\n</entries>"


def parse_response(text):
    text = text.strip()
    summary = ""
    scene = ""
    m = re.search(r"<summary>\s*(.*?)\s*</summary>", text, re.DOTALL | re.IGNORECASE)
    if m:
        summary = m.group(1).strip()
        text = text[: m.start()] + text[m.end() :]
    m = re.search(r"<scene>\s*(.*?)\s*</scene>", text, re.DOTALL | re.IGNORECASE)
    if m:
        scene = m.group(1).strip()
        text = text[: m.start()] + text[m.end() :]

    translations = {}
    current_num = None
    current_lines = []
    state = "number"

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if state == "number":
            m2 = re.match(r"#(\d+)", line)
            if m2:
                if current_num is not None and current_lines:
                    translations[current_num] = "\n".join(current_lines)
                current_num = int(m2.group(1))
                current_lines = []
                state = "translation_start"
        elif state == "translation_start":
            if line.lower().startswith("translation>") or line.startswith("译文>"):
                prefix = 12 if line.lower().startswith("translation>") else 3
                rest = line[prefix:].strip()
                if rest:
                    current_lines.append(rest)
                state = "translation_body"
            elif re.match(r"#(\d+)", line):
                if current_num is not None and current_lines:
                    translations[current_num] = "\n".join(current_lines)
                current_num = None
                current_lines = []
        elif state == "translation_body":
            if re.match(r"#(\d+)", line):
                if current_num is not None and current_lines:
                    translations[current_num] = "\n".join(current_lines)
                m2 = re.match(r"#(\d+)", line)
                current_num = int(m2.group(1)) if m2 else None
                current_lines = []
                state = "translation_start"
            else:
                current_lines.append(line)

    if current_num is not None and current_lines:
        translations[current_num] = "\n".join(current_lines)

    return translations, summary, scene


def call_api(client, model, messages, thinking=False, max_retries=5):
    kwargs = {
        "model": model,
        "messages": messages,
        "timeout": 300,
    }
    if thinking:
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        kwargs["reasoning_effort"] = "high"
    else:
        kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
        kwargs["temperature"] = 1.3

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content, resp.usage
        except Exception as e:
            print(f"  API 错误（第 {attempt + 1} 次）: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(3)
    return None, None


def translate_srt(
    input_path,
    output_path,
    api_key,
    base_url,
    model,
    batch_size=30,
    max_retries=5,
    merge=True,
):
    client = OpenAI(api_key=api_key, base_url=base_url)

    orig_entries = parse_srt(input_path)

    if merge:
        merged_entries = merge_short_entries(orig_entries)
        n_merged = len(orig_entries) - len(merged_entries)
        if n_merged:
            print(
                f"  合并短条目: {len(orig_entries)} → {len(merged_entries)} ({n_merged} 条合并)",
                file=sys.stderr,
            )
        entries = merged_entries
    else:
        entries = orig_entries

    total = len(entries)
    n_batches = (total + batch_size - 1) // batch_size
    print(
        f"  翻译 {pathlib.Path(input_path).name}: {total} 条, {n_batches} 批",
        file=sys.stderr,
    )

    context = {"summary": "", "scene": ""}
    merged_translations = {}
    had_error = False
    t_start = time.time()
    total_prompt = 0
    total_completion = 0
    total_cached = 0

    for b in range(n_batches):
        start = b * batch_size
        end = min(start + batch_size, total)
        batch = entries[start:end]
        batch_text = build_batch_text(batch)

        ctx_parts = []
        if context["scene"]:
            ctx_parts.append(f"<scene>{context['scene']}</scene>")
        if context["summary"]:
            ctx_parts.append(f"<summary>{context['summary']}</summary>")
        ctx_str = ("\n".join(ctx_parts) + "\n") if ctx_parts else ""

        user_content = f"{ctx_str}{batch_text}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        success = False
        for attempt in range(max_retries):
            print(
                f"    [{b + 1}/{n_batches}] 尝试 {attempt + 1}/{max_retries}...",
                file=sys.stderr,
                flush=True,
            )
            result, usage = call_api(client, model, messages)
            if result is None:
                continue
            parsed, summary, scene = parse_response(result)
            matched = sum(1 for i, _, _ in batch if i in parsed)
            if matched == len(batch):
                for i, _, _ in batch:
                    if i in parsed:
                        merged_translations[i] = parsed[i]
                if usage:
                    total_prompt += usage.prompt_tokens or 0
                    total_completion += usage.completion_tokens or 0
                    total_cached += getattr(usage, "prompt_cache_hit_tokens", 0) or 0
                context["summary"] = summary or context["summary"]
                context["scene"] = scene or context["scene"]
                success = True
                break
            else:
                print(
                    f"    行数不匹配: 输入 {len(batch)} 条, 解析到 {matched} 条, 重试",
                    file=sys.stderr,
                )

        if not success:
            print(f"  [ERROR] 第 {b + 1} 批翻译失败", file=sys.stderr)
            had_error = True
            break

    if had_error:
        print(f"  出错终止，未写出输出文件", file=sys.stderr)
        return 1

    out_entries = [(e[0], e[1], merged_translations.get(e[0], "")) for e in entries]
    pathlib.Path(output_path).write_text(compose_srt(out_entries), encoding="utf-8")

    elapsed = time.time() - t_start
    print(f"  完成: {pathlib.Path(output_path).name}", file=sys.stderr)
    print(f"  统计: {n_batches} 批, 用时 {elapsed:.1f}s", file=sys.stderr)
    print(f"    prompt tokens:     {total_prompt:>10,}", file=sys.stderr)
    if total_cached:
        print(f"    缓存命中:          {total_cached:>10,}", file=sys.stderr)
    print(f"    completion tokens: {total_completion:>10,}", file=sys.stderr)
    print(
        f"    合计:              {total_prompt + total_completion:>10,}",
        file=sys.stderr,
    )
    return 0
