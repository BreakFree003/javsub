import configparser
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "javsub"
CONFIG_PATH = CONFIG_DIR / "config"

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"

DEFAULTS = {
    "base_url": "",
    "model": "",
}

TEMPLATE = """# javsub 配置文件
[default]
# API key（必填）
api_key=
# API 地址（可选）
base_url=https://api.deepseek.com
# 模型名（可选）
model=deepseek-v4-flash
"""


def _prompt(label, default=None):
    hint = f" [{default}]" if default else ""
    while True:
        try:
            value = input(f"{label}{hint}: ").strip()
        except EOFError:
            return None
        if value:
            return value
        if default is not None:
            return default
        print("  不能为空，请重新输入")


def interactive_setup():
    print("首次使用，请配置 API：", file=sys.stderr, flush=True)

    api_key = _prompt("API key")
    if api_key is None:
        _write_template()
        return {"api_key": "", "base_url": "", "model": ""}

    base_url = _prompt("API 地址", default=DEFAULT_BASE_URL)
    if base_url is None:
        _write_template()
        return {"api_key": "", "base_url": "", "model": ""}

    model = DEFAULT_MODEL

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    content = (
        f"# javsub 配置文件\n[default]\napi_key={api_key}\nbase_url={base_url}\nmodel={model}\n"
    )
    CONFIG_PATH.write_text(content)
    print(f"已保存配置: {CONFIG_PATH}", file=sys.stderr, flush=True)

    return {"api_key": api_key, "base_url": base_url, "model": model}


def _write_template():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(TEMPLATE)
        print(f"已创建配置文件: {CONFIG_PATH}", file=sys.stderr, flush=True)
    print("请编辑后重新运行。", file=sys.stderr, flush=True)


def load_config():
    config = dict(DEFAULTS)

    if not CONFIG_PATH.exists():
        return interactive_setup()

    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH)
    if "default" in parser:
        for key in ("api_key", "base_url", "model"):
            if key in parser["default"] and parser["default"][key]:
                config[key] = parser["default"][key]
    config["base_url"] = config["base_url"] or DEFAULT_BASE_URL
    config["model"] = config["model"] or DEFAULT_MODEL
    return config
