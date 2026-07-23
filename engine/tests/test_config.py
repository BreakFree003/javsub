import builtins

from engine import config


def _patch_paths(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "javsub"
    monkeypatch.setattr(config, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config, "CONFIG_PATH", cfg_dir / "config")


def test_interactive_setup(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)
    answers = iter(["sk-abc", "", ""])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    result = config.interactive_setup()

    assert result == {
        "api_key": "sk-abc",
        "base_url": config.DEFAULT_BASE_URL,
        "model": config.DEFAULT_MODEL,
    }
    assert config.CONFIG_PATH.exists()
    content = config.CONFIG_PATH.read_text()
    assert "api_key=sk-abc" in content
    assert f"base_url={config.DEFAULT_BASE_URL}" in content
    assert f"model={config.DEFAULT_MODEL}" in content


def test_interactive_setup_empty_api_key_retries(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)
    answers = iter(["", "  ", "sk-abc", "", ""])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    result = config.interactive_setup()

    assert result["api_key"] == "sk-abc"
    assert config.CONFIG_PATH.exists()
    assert "api_key=sk-abc" in config.CONFIG_PATH.read_text()


def test_interactive_setup_eof_fallback(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)

    def raise_eof(_):
        raise EOFError

    monkeypatch.setattr(builtins, "input", raise_eof)

    result = config.interactive_setup()

    assert result == {"api_key": "", "base_url": "", "model": ""}
    assert config.CONFIG_PATH.exists()
    content = config.CONFIG_PATH.read_text()
    assert "api_key=" in content
    assert "base_url=https://api.deepseek.com" in content


def test_load_config_existing(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)
    config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config.CONFIG_PATH.write_text(
        "[default]\napi_key=sk-existing\nbase_url=https://x.com\nmodel=m1\n"
    )

    result = config.load_config()

    assert result == {
        "api_key": "sk-existing",
        "base_url": "https://x.com",
        "model": "m1",
    }


def test_load_config_empty_fields_use_defaults(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)
    config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config.CONFIG_PATH.write_text("[default]\napi_key=sk-x\nbase_url=\nmodel=\n")

    result = config.load_config()

    assert result["api_key"] == "sk-x"
    assert result["base_url"] == config.DEFAULT_BASE_URL
    assert result["model"] == config.DEFAULT_MODEL


def test_load_config_first_run_triggers_setup(monkeypatch, tmp_path):
    _patch_paths(tmp_path, monkeypatch)
    answers = iter(["sk-new", "", ""])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    result = config.load_config()

    assert result["api_key"] == "sk-new"
    assert config.CONFIG_PATH.exists()
