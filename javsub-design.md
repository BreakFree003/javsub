# javsub 设计文档 v1

## 定位

Mac 上转录加翻译 JAV 视频的命令行工具。一个命令出字幕。

## 用法

```bash
javsub video.mp4
```

没有参数。配置放 `~/.config/javsub/config`：

```ini
[default]
api_key=sk-xxx
base_url=https://api.deepseek.com
model=deepseek-v4-flash
asr_model=ph0ryn/Qwen3-ASR-1.7B-JA-MLX-8bit
```

也支持环境变量 `JAVSUB_API_KEY` 等。

## 项目文件

```
engine/
├── javsub.py           # 入口
├── asr.py              # 调 mlx-qwen3-asr
├── translate.py        # 翻译（从现有代码提取）
├── srt_utils.py        # SRT 解析合并
├── config.py           # 配置读写
└── final_prompt.txt    # 内置 prompt
```

## 执行流程

```
javsub video.mp4
  1. 检查 video.zh.srt → 已有则跳过退出
  2. 检查 video.jp.srt → 已有则跳到翻译
  3. ASR → video.jp.srt
  4. 翻译 → video.zh.srt
```

## v1 不做的事

- 参数选项（--config / --skip-asr / --force）
- 输出格式切换（isatty 检测）
- 配置文件安全权限（chmod 600）
- 损坏文件检测
- 视频格式校验
- 批量/目录处理
- macOS GUI App
- IINA 插件

## 测试

```bash
cd engine && python -m pytest tests/
```

测试 srt 解析、翻译响应解析、配置读写。不需要网络和 API key。ASR 模块手动测。
