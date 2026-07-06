import configparser
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "javsub"
CONFIG_PATH = CONFIG_DIR / "config"

DEFAULTS = {
    "base_url": "",
    "model": "",
    "asr_model": "ph0ryn/Qwen3-ASR-1.7B-JA-MLX-8bit",
}

TEMPLATE = """# javsub 配置文件
[default]
# API key（必填）
api_key=
# API 地址（可选）
base_url=https://api.deepseek.com
# 模型名（可选）
model=deepseek-v4-flash
# ASR 模型（可选）
asr_model=ph0ryn/Qwen3-ASR-1.7B-JA-MLX-8bit
"""


def load_config():
    config = dict(DEFAULTS)

    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(TEMPLATE)
        print(f"已创建配置文件: {CONFIG_PATH}", file=sys.stderr)
        print("请编辑后重新运行。", file=sys.stderr)
        return config

    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH)
    if "default" in parser:
        for key in ("api_key", "base_url", "model", "asr_model"):
            if key in parser["default"] and parser["default"][key]:
                config[key] = parser["default"][key]
    return config
