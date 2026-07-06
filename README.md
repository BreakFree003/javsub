# javsub

Mac 上一键转录 + 翻译 JAV 视频的命令行工具。一个命令输出中文字幕。

## 安装

```bash
git clone https://github.com/BreakFree/javsub.git
cd javsub
pip install -e .
```

## 依赖

- Python 3.10+
- Apple Silicon Mac（MLX 依赖）
- 兼容 OpenAI 的 API key（用于翻译）

## 配置

`~/.config/javsub/config`：

```ini
[default]
api_key=sk-xxx
base_url=https://api.deepseek.com
model=deepseek-v4-flash
asr_model=ph0ryn/Qwen3-ASR-1.7B-JA-MLX-8bit
```

环境变量 `JAVSUB_API_KEY` / `JAVSUB_BASE_URL` / `JAVSUB_MODEL` 可覆盖配置文件。

## 用法

```bash
javsub video.mp4
```

输出 `video.zh.srt`。如果已存在则跳过，只需翻译日文字幕可提前放入 `video.jp.srt`。

## 项目结构

```
engine/
├── javsub.py         # 入口
├── asr.py            # ASR 转录（mlx-qwen3-asr）
├── translate.py      # 翻译（OpenAI 兼容 API）
├── srt_utils.py      # SRT 解析与合并
├── config.py         # 配置读写
└── final_prompt.txt  # 翻译 prompt 模板
```

## License

MIT
