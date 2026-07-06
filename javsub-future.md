# javsub 后续规划

## Phase 2: macOS GUI App

现有 CLI 足够用之后再做。一个 SwiftUI 壳子，通过 Process 调同一套 Python 引擎，stdout 读 JSON 进度。

### 带来什么

- 用户不用碰终端
- 拖拽视频 → 出字幕
- 进度条
- 首次启动配置页

### 技术要点

- 捆绑 python-build-standalone 解决 Python 依赖
- 首次启动创建 venv + pip install + 下载模型
- macOS 15+ / Apple Silicon 限定
- 不上 Mac App Store，走 GitHub Releases .dmg

### 什么时候做

等 Phase 1 CLI 有人用、反馈够了再动手。

---

## Phase 3（待定）

根据实际需求决定要不要做：

| 功能 | 触发条件 |
|------|---------|
| 批处理/目录扫描 | 用户反馈处理多个视频不方便 |
| 文件夹监控（Watch Folder） | 同上 |
| IINA 插件 | 用户想要播放器内直接看字幕 |
| Windows/Linux | 除非有人贡献移植 |

---

## 不做的事

| 功能 | 原因 |
|------|------|
| Mac App Store | 架构不允许 |
| 钥匙串存 API key | 个人工具不需要 |
| uncensored API fallback | base_url 可配置，有需要自己改 |
| 字幕编辑/预览 | 超出"生成"范围 |
