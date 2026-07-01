import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "javsub"
CONFIG_PATH = CONFIG_DIR / "config"

DEFAULTS = {
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-v4-flash",
    "asr_model": "ph0ryn/Qwen3-ASR-1.7B-JA-MLX-8bit",
}


def load_config():
    config = dict(DEFAULTS)

    if CONFIG_PATH.exists():
        parser = configparser.ConfigParser()
        parser.read(CONFIG_PATH)
        if "default" in parser:
            for key in ("api_key", "base_url", "model", "asr_model"):
                if key in parser["default"]:
                    config[key] = parser["default"][key]

    return config
