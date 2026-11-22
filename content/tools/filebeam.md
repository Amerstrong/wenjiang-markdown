---
title: FileBeam Lite
slug: filebeam
name: FileBeam Lite
tagline: 手机零安装的局域网文件互传工具
summary: FileBeam Lite 是一款面向电脑与手机的免费开源局域网文件互传工具。电脑启动服务后，手机扫码即可打开浏览器收发文件，不经过公网中转。
category: 跨设备效率
status: 免费开源
version: "1.0.4"
platform: Windows 10 / 11
price: "19.9"
price_label: Lite 免费 / Pro 个人终身 ¥19.9
is_free: true
license_label: MIT
download_url: https://github.com/Amerstrong/FileBeam_Lite/releases/latest
download_label: 下载 FileBeam Lite
repo_url: https://github.com/Amerstrong/FileBeam_Lite
featured: true
pain: 手机与电脑临时传文件时，登录账号、安装 App 或上传公网云盘都太慢。
quick_take: 适合同一 Wi-Fi 下快速传照片、PDF、Word 和安装包。手机端无需安装 App，数据通过局域网直连；免费 Lite 版单文件上限 10 MB。
seo_title: FileBeam Lite｜免费开源的手机电脑局域网文件互传工具
seo_description: FileBeam Lite 是免费开源的局域网文件互传工具，PC 启动服务后手机扫码即用，无需安装 App，文件不经过第三方公网服务器，支持 Windows 10/11。
keywords:
  - FileBeam Lite
  - 局域网文件互传
  - 手机电脑传文件
  - 扫码传文件
  - 免费开源
  - LocalSend替代
  - 离线文件传输
features:
  - 手机零安装，扫码即用
  - 局域网直连，不经过公网
  - Windows 免费开源
  - 支持上传与共享下载
---

## 一句话认识 FileBeam Lite

**FileBeam Lite** 是一款免费开源的局域网文件互传工具。电脑端启动服务后，屏幕会显示局域网访问地址与二维码；手机连接同一个 Wi-Fi，用相机或浏览器扫码，就能打开轻量文件页面，把照片、文档或安装包直接传给电脑。

电脑发往手机的流程同样简单：把文件放进共享目录，手机刷新页面即可下载。整个过程不需要在手机安装 App，不需要登录账号，也不把文件上传到第三方公网服务器。

<div class="feature-grid">
  <div class="feature-item"><strong>📱 手机零安装</strong><span>安卓与 iPhone 均可直接使用浏览器访问。</span></div>
  <div class="feature-item"><strong>🔗 局域网直连</strong><span>同一 Wi-Fi 或手机热点下即可传输，不依赖公网。</span></div>
  <div class="feature-item"><strong>📤 双向互传</strong><span>手机上传到电脑，电脑共享文件给手机下载。</span></div>
  <div class="feature-item"><strong>🛡️ 数据少中转</strong><span>文件只在当前局域网设备之间传递。</span></div>
</div>

## 为什么做 FileBeam

临时传几张照片或一份 PDF，经常会遇到额外成本：

- 聊天软件会压缩图片，文件过大时还会限制发送。
- 登录微信、QQ 或网盘账号需要双方配合，临时设备尤其麻烦。
- LocalSend 等工具体验不错，但接收端通常也要安装 App。
- 企业 Wi-Fi 可能关闭设备发现或组播，导致部分工具搜不到设备。

FileBeam 选择 HTTP + 浏览器作为基础通道。只要手机能访问电脑的局域网 IP，就可以打开页面。它不追求变成完整网盘，而是把“临时互传”这个动作做得足够直接。

## 使用流程

1. 从 GitHub Release 下载 Windows 压缩包并解压。
2. 运行 `FileBeam_Lite.exe`，等待本地服务启动并打开浏览器。
3. 让手机和电脑连接同一个 Wi-Fi，或让电脑连接手机热点。
4. 用手机相机扫描电脑页面上的二维码。
5. 手机页面即可上传文件到 `received`，或从 `shared` 下载电脑共享文件。

<div class="notice"><strong>网络要求：</strong>FileBeam Lite 通过局域网 HTTP 服务工作。请仅在可信的家庭、个人热点或办公网络中使用，不要把端口直接暴露到公网。</div>

## 免费 Lite 版下载

FileBeam Lite 以 MIT 许可证免费开源。最新版本、发布说明和校验文件统一归档在 GitHub：

<div class="inline-cta">
  <div><strong>免费 Lite 版</strong><span>Windows 10 / 11 · 解压即用 · 手机端无需安装。</span></div>
  <a class="button accent" href="https://github.com/Amerstrong/FileBeam_Lite/releases/latest" target="_blank" rel="noopener noreferrer">前往 GitHub Release →</a>
</div>

下载后建议核对 Release 中的 `SHA256SUMS.txt`，确认安装包完整且与官方发布一致。

## 免费版 vs 专业版（19.9 元）

| 能力 | FileBeam Lite（免费） | FileBeam Pro（¥19.9） |
| --- | --- | --- |
| 单文件大小 | 10 MB | 大文件传输，面向数百 MB、GB 乃至更大文件 |
| 单文件发送 | 支持 | 支持 |
| 文件夹批量传输 | 不支持，仅按文件传输 | 支持文件夹选择、目录浏览与批量传输 |
| 批量下载 / ZIP | 逐个文件下载 | 支持批量接收与目录打包 ZIP |
| 断点续传 | 不支持 | 支持分块传输、断网续传与弱网重试 |
| 手机屏幕常亮 | 不支持 | 传输期间自动保持屏幕常亮，降低锁屏中断风险 |
| 传输历史 | 当前浏览器最近记录 | 完整历史与 24 小时 / 3 天 / 7 天 / 会话清理策略 |
| 自定义固定端口 | 不支持可视化设置 | 支持自定义并固定局域网服务端口 |
| 使用场景 | 日常照片、PDF、Word 与小文档 | 视频、设计素材、批量图片、开发资源与团队办公 |
| 授权方式 | 免费开源，MIT 许可证 | 个人终身买断授权，支持个人多设备使用，重装系统/换机不失效 |

> Lite 版继续免费开放，适合轻量互传；Pro 版面向大文件、批量素材和长期使用场景。购买前建议先确认 Lite 版是否已满足需求。

## 支付宝扫码购买与激活码获取

<div class="qr-grid">
  <div class="qr-card">
    <img src="/assets/filebeam-alipay-19.9.png" alt="AI探索者支付宝经营收款码，FileBeam Pro 价格 19.9 元">
    <span>FileBeam Pro ¥19.9 · 支付宝</span>
  </div>
  <div class="qr-card">
    <img src="/assets/wechat-19.9.png" alt="FileBeam Pro 19.9 元微信收款码">
    <span>FileBeam Pro ¥19.9 · 微信</span>
  </div>
</div>

购买与激活流程：

1. 根据支付方式扫描上方二维码，支付 `¥19.9`。
2. 将付款截图和联系邮箱发送至 [xiaoyu12657@qq.com](mailto:xiaoyu12657@qq.com)。
3. 后台核验后下发 FileBeam 激活码，不需要提供硬件机器码。
4. 打开 FileBeam Lite，进入“升级专业版”，输入激活码并点击验证。
5. 首次联网验证通过后，客户端在本地用户目录保存带签名的授权凭证，后续离线启动无需再次联网。

<div class="inline-cta">
  <div><strong>已经付款但暂未收到激活码？</strong><span>请附付款截图和联系邮箱发送邮件，我们会人工核对并补发。</span></div>
  <a class="button" href="mailto:xiaoyu12657@qq.com">联系客服 →</a>
</div>

<div class="notice"><strong>授权说明：</strong>FileBeam Pro 为个人终身买断授权，支持个人多设备使用，不绑定单台硬件，重装系统或换机不会失效。同一激活码最多完成 10 次联网激活校验；首次校验成功后可在离线状态继续使用。请勿在公开页面、聊天群或 Issue 中发布自己的完整激活码。</div>

## 双子星捆绑包

如果同时需要跨设备互传和 AI 内容转 Word，可以选择 **¥29.8 双子星捆绑包**：

<div class="purchase-grid">
  <div class="price-card featured">
    <div class="tag-row"><span class="tag warm">双子星 BUNDLE</span></div>
    <h3>FileBeam Pro + 文匠</h3>
    <div class="price">¥29.8</div>
    <ul>
      <li>FileBeam 专业版：个人多设备终身版，重装系统/换机不失效</li>
      <li>文匠 Markdown_Office：支持绑定 3 台设备的终身版</li>
      <li>两套软件分别下发独立激活码</li>
    </ul>
    <p><a class="button accent" href="/buy.html">查看双子星购买页 →</a></p>
  </div>
  <div class="qr-card">
    <img src="/assets/bundle-alipay-29.8.png" alt="FileBeam 与文匠双子星捆绑包 29.8 元支付宝收款码">
    <span>双子星捆绑包 ¥29.8 · 支付宝</span>
  </div>
</div>

> 微信暂时只提供 FileBeam Pro 19.9 元收款码，复用原有微信收款码；双子星捆绑包请使用支付宝 29.8 元经营码。

## 免费版功能与边界

当前 Lite 版定位为日常轻量互传：

| 能力 | FileBeam Lite |
| --- | --- |
| 手机端安装 | 无需安装 App |
| 传输通道 | 同一局域网 HTTP 直连 |
| 单文件上限 | 10 MB |
| 手机上传到电脑 | 支持 |
| 电脑共享文件到手机 | 支持 |
| Windows 运行 | 解压即用 |
| 数据经过公网服务器 | 不经过 |

Lite 版适合照片、论文、PDF、Word 文档、发票和小型安装包。超大视频、断点续传和长时间弱网传输属于后续增强方向。

## 隐私与安全

- 文件只在当前局域网设备之间传输。
- 不需要注册账号，不上传文件到第三方云盘。
- 接收和共享目录位于解压后的程序目录。
- 服务关闭后，局域网页面即停止访问。
- 传输内容不会自动写入公网服务。

## 工程与发布

FileBeam Lite 的 Windows 发布包经过自动启动测试、首页访问测试和文件上传测试。仓库同时提供构建说明、MIT 许可证与每个版本的 SHA256 校验文件。

如果你希望了解从源码到 GitHub Release 的完整工程过程，可以阅读技术专栏中的 [Python 工具打包、测试与 GitHub Release 实战](/posts/filebeam-python-release-pipeline.html)。

