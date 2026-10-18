# Audio Link V2 · v2.0.0

发布日期 / Release date: **2026-10-18**

## 中文

本次将最新版整理为可分发的 MIT 开源源码包，不是免安装可执行程序。
保留上游版权和许可证；与 Apple、Microsoft 或 OpenAI 无官方关联。

### V2 功能

- 电脑 WASAPI 音频采集、无损 PCM 聆听和兼容 Opus 线路，默认自动。
- 苹果风格分段控件：自动／无损／兼容；桌面与浏览器均可点击并双向同步。
- 两端可展开的连接详情，显示实际格式及接收端上报的缓冲、丢包或缺帧。
- 悬浮窗、任务栏和托盘控制、窗口缩放、设备别名记忆，以及九种语言。

PCM 无损指采集后的 16 位单／双声道数据未经有损编码传输，
不代表原始音源端到端位完美、24 位 Hi-Res 或零延迟。
仅供可信局域网使用，无登录认证，不要公开端口。模式切换可能短暂重连。

### 安装和升级

1. 解压压缩包，进入其中的 `audio-link` 文件夹。
2. 在 Windows 10/11 安装 Python 3.12，运行 `setup.cmd`，再运行 `start.cmd`。
3. 接收设备打开悬浮窗提供的 HTTPS 地址，确认属于自己的电脑后自行处理证书提示。
4. 升级前停止旧版音频服务。仅在本机按需迁移自己的 `data` 记录，不要将其提交到 GitHub。
5. 升级后刷新所有接收网页，重新生成快捷方式，避免仍启动旧版目录。

推荐使用 Codex 辅助部署，完整提示词见 [项目说明](../README.md)。
旧的平铺目录安装应按使用说明迁移，不要直接混合复制新旧源码。

### 上传 GitHub

将解压后的 `audio-link` 文件夹内的源码作为仓库根目录上传，包括 `app`、`web`、
`assets`、`docs`、`scripts`、`tests`、`.github`、`VERSION`、说明文件和 MIT 许可证。
图片与图标已经集中在 `assets`。不要上传本机正在使用的 `data`、`.venv` 或证书。

建议发布标签为 `v2.0.0`，Release 附件上传：

- `audio-link-v2.0.0-source.zip`
- `SHA256SUMS-v2.0.0.txt`

本次仅在本地打包，没有自动创建 GitHub 仓库、推送源码或发布 Release。

## English

This is the **v2.0.0 MIT-licensed source release**, not a standalone executable.
Upstream attribution is retained. There is no official affiliation with Apple,
Microsoft or OpenAI.

### Included

- Windows WASAPI capture with lossless PCM listening and compatible Opus; Auto by default.
- Apple-inspired segmented controls, editable and synchronized on desktop and browser.
- Expandable connection diagnostics with actual formats and receiver-reported metrics.
- Floating/taskbar/tray controls, scaling, device aliases and nine languages.

Lossless means no lossy codec after 16-bit mono/stereo capture, not original-source
bit-perfect playback, 24-bit Hi-Res or zero latency. This unauthenticated tool is for
trusted LANs only. Never expose its port publicly. Mode changes can briefly reconnect.

Extract the archive, enter `audio-link`, then run `setup.cmd` and `start.cmd` on
Windows 10/11 with Python 3.12. Stop older services before upgrading, keep private
runtime data local, recreate shortcuts and refresh receiver pages. Do not mix a
legacy flat-layout installation with the new source tree. Codex-assisted setup
instructions are available in the [English README](../README.en.md).

For GitHub, upload the extracted folder's **contents as the repository root**,
including hidden project files, `VERSION`, documentation and license. Artwork is
under `assets`. Exclude local runtime state, virtual environments and private keys.
Use the suggested tag `v2.0.0` and attach the versioned source ZIP and checksum file.
Packaging alone does not create a GitHub repository, push commits or publish a release.

## 检验 / Verification

```powershell
.venv\Scripts\python.exe scripts/run_tests.py
.venv\Scripts\python.exe scripts/package_source.py
.venv\Scripts\python.exe scripts/verify_source_archive.py
Get-FileHash .\dist\audio-link-v2.0.0-source.zip -Algorithm SHA256
```

打包允许列表排除运行数据、私钥、日志、虚拟环境和 Git 历史。
验证程序检查 SHA-256、压缩包完整性、文件允许列表及解压后运行的测试。

The packager excludes runtime state, private keys, logs, virtual environments and
Git history. Verification checks SHA-256, ZIP integrity, exact allowlist membership
and tests run from a newly extracted copy.
