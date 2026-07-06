import sys
from pathlib import Path

from .config import load_config
from .asr import run_asr
from .translate import translate_srt


def main():
    if len(sys.argv) != 2:
        print(f"用法: {Path(sys.argv[0]).name} <video.mp4>", file=sys.stderr)
        sys.exit(1)

    video = Path(sys.argv[1])
    if not video.exists():
        print(f"文件不存在: {video}", file=sys.stderr)
        sys.exit(4)

    config = load_config()
    if not config.get("api_key"):
        print("错误: 未设置 API key", file=sys.stderr)
        print("  在 ~/.config/javsub/config 中配置 API key", file=sys.stderr)
        sys.exit(3)

    jp_path = video.with_suffix(".jp.srt")
    zh_path = video.with_suffix(".zh.srt")

    if zh_path.exists():
        print(f"已存在: {zh_path}", file=sys.stderr)
        sys.exit(0)

    if not jp_path.exists():
        print(f"ASR: {video.name}", file=sys.stderr)
        if not run_asr(video, config):
            sys.exit(1)
    else:
        print(f"ASR 已存在: {jp_path.name}", file=sys.stderr)

    print(f"翻译: {jp_path.name}", file=sys.stderr)
    rc = translate_srt(
        str(jp_path),
        str(zh_path),
        api_key=config["api_key"],
        base_url=config["base_url"],
        model=config["model"],
    )
    if rc != 0:
        sys.exit(2)

    print(f"完成: {zh_path.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
