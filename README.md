# Audio Link V2

**v2.0.0 · 2026-10-18** · [V2 发布说明 / Release notes](docs/RELEASE-v2.md)

**让 Windows 电脑的声音，自由流转到浏览器。**

Apple 风格悬浮控制窗与响应式网页接收端，适合手机、平板和另一台电脑。
无需移动端 App、账号或云服务器。MIT 开源。

Stream Windows system audio to a browser on your phone, tablet or another computer.
No mobile app, account or cloud server required. MIT licensed.

[English overview](#english-overview) · [Full English README](README.en.md) · [中文教程](docs/USAGE.zh-CN.md) · [English guide](docs/USAGE.en.md) · [安全说明 / Security](SECURITY.md)

![通用网页接收端](assets/screenshots/receiver.png)

## 功能

- Windows WASAPI 系统音频采集，优先 PCM 无损传输，兼容 WebRTC / Opus。
- 置顶悬浮窗、任务栏最小化、托盘控制、75%–130% 缩放与右下角停靠。
- 名称旁的铅笔图标原位编辑；浏览器随机标识实现每台设备的名称记忆。
- 简繁中文、英语、法语、德语、西班牙语、日语、韩语、俄语。
- 网页约每两秒跟随桌面语言设置，不重建音频连接。
- 可选麦克风反向传输、连接详情、前台保活请求。

![桌面悬浮窗](assets/screenshots/desktop.png)

## 推荐：使用 Codex 辅助部署 / Recommended: deploy with Codex

**本项目推荐使用 Codex 辅助本地部署和排查问题。** 在 Windows 发送电脑上，
用 Codex 打开当前仓库目录，将下面的提示词发给它即可开始。
应使用能访问这台 Windows 电脑的本地工作环境，而不是仅在云端准备源码。
Codex 是可选部署助手，不是本项目的运行依赖，也不代表官方认证。

```text
请先阅读当前 Audio Link 仓库的 README、使用说明和安全说明，
帮我在这台 Windows 电脑本地部署。检查 Python 3.12、音频输出设备和端口占用，
在项目 .venv 中安装 requirements.txt，运行默认测试，并创建桌面快捷方式。
启动悬浮窗并验证音频服务可访问，告诉我手机、平板或另一台电脑应该打开的地址。
保留已有设备名称记录，不覆盖无关文件，不关闭防火墙、不做公网映射。
涉及管理员权限、防火墙规则、浏览器证书提示或麦克风授权时，说明用途并让我确认或操作。
最后给出中英文的启动、停止、重连和常见问题说明；没有验证的项目请明确标注。
```

**We recommend Codex for assisted local deployment and troubleshooting.**
Open this repository in a Codex environment with access to the Windows sender,
then use this prompt. Codex is optional, not a runtime dependency or an endorsement.

```text
Read this Audio Link repository's README, usage guide and security notes first.
Deploy it locally on this Windows PC. Check Python 3.12, playback devices and port conflicts.
Install requirements.txt in the project .venv, run the default tests and create a desktop shortcut.
Open the controller, verify the audio service, and report the receiver URL for other devices.
Preserve existing device aliases and unrelated files. Do not disable the firewall or expose public ports.
Explain and ask me to confirm or complete admin, firewall, certificate and microphone permission steps.
Finish with bilingual start/stop/reconnect instructions and clearly identify anything not verified.
```

Codex 的界面与权限配置请以 [OpenAI 官方文档](https://learn.chatgpt.com/docs/app) 为准。
不使用 Codex 时，按照下面的手动步骤同样可以部署。

## 手动快速开始

### 无损与兼容

桌面和网页都提供 **自动（优先无损）／无损 PCM／兼容 Opus** 选择，默认自动。
任一端修改后，约 2–3 秒内同步到其他端；选择保存在电脑，语言修改不会清空模式。
此设置全局影响所有新版聆听接收端，麦克风仍使用 Opus。手动切换会短暂重连；浏览器要求播放授权时需点按按钮。
两端都只显示实际模式，不显示音质上限宣传文字。展开“连接详情”可看各设备格式、播放缓冲、丢包或缺帧数据。
桌面每约 3 秒刷新浏览器上报的数据，超过 10 秒未更新的数值显示为未知，而非实时测量。
未连接、协商中和旧版未知状态不会显示成无损。
自动模式在功能不支持、连接失败或缓冲溢出时回退 Opus，并显示原因；强制 PCM 模式只报错，不偷偷降级。
PCM 是采集后的 **16 位、单声道或双声道**原始数据，采样率跟随输出设备。
48 kHz 双声道约 **1.536 Mb/s**（不含网络开销）。采集、系统混音、环绕声降混和播放端重采样不在无损保证内，
不宣称原始音源端到端位完美，也不将 16 位采集宣传为 24 位 Hi-Res。
无损播放需要 HTTPS 安全上下文和 AudioWorklet；普通局域网 HTTP 可使用兼容 Opus。
连接详情显示实际 PCM 格式、播放缓冲和累计播放缺帧次数。网络抖动、锁屏或时钟漂移仍可能造成中断。
麦克风反向传输保持 Opus，不是无损模式。开发者可用 `node tests/test_worklet.js` 验证播放器样本处理。

发送电脑需要 **Windows 10/11、Python 3.12**，并启用一个音频输出设备。
接收端需要支持 WebRTC 音频的现代浏览器。Safari、Chrome、Edge、Firefox
均可尝试；具体功能仍受系统、浏览器和权限限制。

1. 下载并解压源码，或克隆仓库。
2. 安装 Python 3.12，确保包含 Windows `py` 启动器。
3. 双击 `setup.cmd` 创建独立虚拟环境并安装依赖。
4. 双击 `start.cmd` 打开悬浮窗，点击“启动音频传输”。
5. 接收设备连接同一路由器，用浏览器打开悬浮窗中的 HTTPS 地址。
6. 仅在确认地址属于自己的电脑后，手动处理本地自签名证书提示。
7. 点击“聆听 → 开始聆听”；需要结束时点击“断开连接”。

不要同时运行本项目和其他占用 `8787` 端口的安装副本。
需要桌面快捷方式时，在安装完成后运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create_shortcut.ps1
```

安装和启动不需要管理员权限。**程序不会自动修改防火墙、开机启动或公开端口。**
防火墙的可选设置请见使用说明。

## 项目结构

```text
app/                 Python 桌面端、音频服务、翻译和设备记录逻辑
web/                 网页 HTML / CSS / JavaScript，无构建工具依赖
assets/icons/        应用图标
assets/screenshots/  文档截图，使用示例数据
docs/                使用说明与架构说明
scripts/             安装、启动、快捷方式、测试和源码打包
tests/               界面、语言、设备记忆、API 与可选音频集成测试
.github/workflows/   Windows CI
data/                本地自动生成；证书、日志和设备记录，不纳入 Git
```

## 开发与测试

```powershell
.venv\Scripts\python.exe scripts/run_tests.py
.venv\Scripts\python.exe scripts/run_tests.py --audio-hardware
node --check web/receiver.js
.venv\Scripts\python.exe scripts/package_source.py
```

默认测试不要求音频硬件；第二条会打开 WASAPI 设备并建立真实本地 WebRTC 会话。
测试使用临时数据目录，不修改日常设备记录。
源码包输出到 `dist/audio-link-v2.0.0-source.zip`，校验文件为 `dist/SHA256SUMS-v2.0.0.txt`。
打包采用允许列表，不包含 `.git`、虚拟环境、`data` 或密钥。

## 边界与安全

- 不保证零延迟；网页“播放缓冲”不是端到端延迟。
- 锁屏、后台播放及屏幕常亮请求是否生效，取决于浏览器和操作系统。
- 没有登录或访问密码，只适合可信局域网，不要映射到公网。
- 浏览器随机标识仅用于记住名称，不是身份验证；清理网站数据、换浏览器
  或更换访问地址后，可能需要重新命名。
- 发送端目前只支持 Windows；接收网页不限定 iOS、Android 或设备品牌。
- 麦克风模式必须由用户授权；普通聆听不需要麦克风权限。

本项目衍生自 [Azec-Zuckerberg/pc-audio-to-iphone](https://github.com/Azec-Zuckerberg/pc-audio-to-iphone)。
保留上游 MIT 版权声明，新增桌面界面、设备名称记忆、多语言同步和新版网页。
与 Apple、Microsoft 或浏览器厂商无关联。

## English overview

Audio Link streams Windows audio to a modern WebRTC-capable browser over a trusted LAN.
The sender runs on Windows 10/11 with Python 3.12; receivers may be phones, tablets
or computers. Audio Link includes a floating controller, taskbar/tray controls,
device aliases, nine languages and a responsive browser UI.

### Recommended: Codex-assisted setup

Use the English prompt in the bilingual Codex section above on the Windows sender.
Codex is a recommended optional setup assistant; Audio Link does not depend on
Codex, an OpenAI API connection or a cloud server to stream audio.
Review permission requests yourself; never expose the unauthenticated service publicly.

### Manual setup

1. Install Python 3.12 with the Windows `py` launcher.
2. Run `setup.cmd`, then `start.cmd`.
3. Start streaming in the desktop controller.
4. Open the displayed HTTPS address on a device connected to the same router.
5. Verify that the address belongs to your PC before manually handling its local
   certificate prompt. Choose Listen, then start playback.

No zero-latency or lock-screen playback guarantee is provided. The service has
no authentication and must stay on a trusted LAN. Do not commit the `data/`
directory, device records, certificates or logs.

See the [English README](README.en.md) and [English usage guide](docs/USAGE.en.md)
for development commands, troubleshooting and optional firewall configuration.
