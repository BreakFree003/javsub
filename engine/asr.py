import subprocess
import sys
from pathlib import Path


def run_asr(video_path, config):
    video = Path(video_path)
    output_dir = video.parent

    print("  转录中...", file=sys.stderr, flush=True)

    cmd = [
        "mlx-qwen3-asr",
        str(video),
        "--model",
        config["asr_model"],
        "--language",
        "Japanese",
        "--output-format",
        "srt",
        "--output-dir",
        str(output_dir),
        "--quiet",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"  ASR 失败 (exit code {result.returncode})", file=sys.stderr)
        return False

    tmp_srt = output_dir / f"{video.stem}.srt"
    jp_srt = output_dir / f"{video.stem}.jp.srt"

    if tmp_srt.exists():
        tmp_srt.rename(jp_srt)
        print(f"  -> {jp_srt.name}", file=sys.stderr)
        return True

    print(f"  ASR 失败: 未生成 SRT 文件", file=sys.stderr)
    return False
