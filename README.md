# 文匠 Wenjiang

<p align="center">
  <img src="logo.png" alt="文匠 Logo" width="200"/>
</p>

<p align="center">
  <strong>GPT Content to Word Converter with Stable Code Block Formatting</strong>
</p>

<p align="center">
  GPT 内容转 Word 专业排版工具 | 稳定保留代码块格式 | 支持 26+ 编程语言 | 一键转换
</p>

<p align="center">
  <a href="#📥-下载">下载</a> •
  <a href="#🚀-快速开始">使用</a> •
  <a href="#-相关资源">文档</a> •
  <a href="README_EN.md">English</a>
</p>

[![Downloads](https://img.shields.io/github/downloads/xiaoyu12657/wenjiang-markdown/total?color=blue)](https://github.com/xiaoyu12657/wenjiang-markdown/releases)
[![GitHub stars](https://img.shields.io/github/stars/xiaoyu12657/wenjiang-markdown)](https://github.com/xiaoyu12657/wenjiang-markdown)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 什么是文匠？

文匠（Wenjiang）是一个专门解决 Markdown 转 Word 时代码块格式混乱、缩进丢失痛点问题的工具。通过精心设计的段落与字符样式模板，文匠可以在转换过程中完美保留代码的原始缩进、等宽字体、灰底框线以及语法高亮，为您实现一键式的专业级技术文档排版。

---

## ❓ 这个工具解决什么问题？

### 问题场景
当你需要将包含代码的 Markdown 文档转换为 Word (.docx) 格式时，通常会遇到以下糟糕的体验：

- ❌ **代码块显示为普通段落** - 所有代码挤成一行，格式全乱。
- ❌ **缩进全部丢失** - Python/YAML 等极其依赖缩进的代码变得完全无法阅读。
- ❌ **没有背景色区分** - 代码和正文混在一起，视觉上极难区分。
- ❌ **字体不是等宽** - 代码对齐混乱，非等宽字体导致排版极其难看。
- ❌ **语法高亮丢失** - 黑白一片，阅读效率极低。

### 典型用户
- 📝 **程序员**：需要提交 Word 格式的技术方案、开发文档或汇报材料。
- 🎓 **学生**：用 Markdown 撰写论文/实验报告，但学校或导师要求提交 Word 格式。
- 📊 **产品经理/技术支持**：需要将技术文档或 API 说明转换为 Word 报告交付给客户。
- 📚 **技术作家/编辑**：编写技术书籍或专栏，需要交付符合排版要求的 Word 稿件。

---

## ✅ 文匠如何解决这个问题？

### 核心技术方案

文匠基于 Pandoc 引擎，但通过预配置深度优化的 Word 模板，实现了开箱即用的完美代码块排版：

```
传统 Pandoc 转换：
Markdown ────> Pandoc ────> Word (代码样式混乱、无背景色、非等宽字体)

文匠转换：
Markdown ────> Pandoc + 优化模板 ────> Word (完美格式、优雅底色、保留高亮)
                             │
                        【 关键差异 】
                        - SourceCode 样式预设
                        - 浅灰色背景色 (#F5F5F5)
                        - Consolas 等宽字体
                        - 代码块精致边框与内边距
                        - 行内代码高亮（玫红字灰底）
```

### 效果对比

**转换前（Pandoc 默认 / 复制粘贴）：**
```text
def hello(): print("混乱的格式")
```

**转换后（文匠）：**
```python
def hello():
    print("完美的灰底代码块")
```
👉 [查看实际效果截图](examples/screenshots/)

---

## 📥 下载

当前版本：**v1.61**

- [立即下载 (GitHub Releases)](https://github.com/xiaoyu12657/wenjiang-markdown/releases)
- [本地备用下载 (百度网盘)](链接)
- [Windows 版本完整安装包](链接) - `文匠_v1.61_完整版.zip` (67MB)

系统要求：Windows 10 / 11

---

## 🚀 快速开始

### 1. GUI 客户端使用 (4步)

1. 从[下载](#📥-下载)部分下载 `文匠_v1.61.exe` 或完整压缩包。
2. 双击运行 `文匠_v1.61.exe`（绿色软件，无需安装）。
3. 选择需要转换的 `.md` 文件。
4. 点击“转换”按钮，即可在同目录下生成排版完美的 `.docx` 文档。

### 2. 命令行版本（高级用户）

如果你倾向于在终端中操作或需要进行自动化集成，可以直接使用命令行：

```bash
# 方法一：使用文匠内置模板和 Pandoc 命令行
pandoc input.md -o output.docx \
  --reference-doc=templates/office_basic.docx \
  --highlight-style=tango

# 方法二：直接使用文匠命令行工具
wenjiang input.md output.docx
```

---

## 🆚 与其他方案对比

| 方案 | 代码格式 | 配置难度 | 稳定性 | 推荐度 |
|------|---------|---------|--------|--------|
| **手动复制粘贴** | ❌ 格式混乱 | 简单 | 差 | ⭐ |
| **Pandoc 默认转换** | ⚠️ 排版不稳定 | 复杂 | 中 | ⭐⭐ |
| **在线转换工具** | ❌ 丢失代码格式 | 简单 | 差 | ⭐⭐ |
| **Pandoc + 自定义模板** | ✅ 完美保留 | 很复杂 (需手动调样式) | 好 | ⭐⭐⭐⭐ |
| **文匠 (Wenjiang)** | ✅ 完美保留 | **零配置 (开箱即用)** | 好 | ⭐⭐⭐⭐⭐ |

👉 [查看详细对比文档](docs/comparison.md)

---

## 📚 支持的编程语言

文匠已对以下 **26+ 种主流编程语言** 进行了完整的排版测试与语法高亮覆盖：

- ✅ **后端/系统开发**：Python, Java, Go, Rust, C/C++, C#, Ruby, PHP
- ✅ **前端开发**：JavaScript, TypeScript, HTML, CSS
- ✅ **移动开发/其他**：Swift, Kotlin, Dart
- ✅ **数据与配置**：SQL, JSON, YAML, XML, TOML
- ✅ **脚本与文档**：Bash, PowerShell, Markdown, LaTeX
- ✅ 更多语言持续测试并完美支持中...

👉 [查看测试报告](docs/test-report.md)

---

## ❓ 常见问题（FAQ）

### Q1: 为什么我用 Pandoc 转换代码块时没有底色和字体格式？
**A:** Pandoc 默认生成的 Word 文档中，`SourceCode` 样式仅绑定了基本的段落缩进，未配置背景填充色和等宽字体。文匠的核心价值在于提供了一套精心调优的 `SourceCode` 样式模板，转换时自动应用该模板，使代码块获得完美的视觉效果。

### Q2: 转换后的 DOCX 文件中，代码块为什么依然是乱的？
**A:** 请确认以下三点：
1. 您的 Markdown 文档中，代码块是否使用了三个反引号（\`\`\`）进行包裹。
2. 每一个代码块是否都指定了正确的语言类型（例如 \`\`\`python）。
3. 转换时是否使用了文匠提供的默认模板或通过文匠客户端进行转换。

### Q3: 可以自定义代码块的背景色和字体吗？
**A:** 可以。文匠完全支持自定义。您只需用 Microsoft Word 打开 `templates/office_basic.docx` 模板文件，修改其中的 `SourceCode` 样式（如修改段落背景色、边框或字体大小），保存后再次转换时指定该模板即可。

### Q4: 文匠支持哪些操作系统？
**A:** 目前文匠图形界面（GUI）客户端仅支持 Windows 10 及 Windows 11。对于 macOS 和 Linux 用户，我们提供了支持命令行的核心转换脚本与模板，您可以通过命令行使用。

### Q5: 行内代码（Inline Code）在 Word 中会如何显示？
**A:** 在 Markdown 中使用单个反引号包裹的行内代码（如 \`code\`），在转换后将自动映射为 `Verbatim Char` 样式，显示为优雅的玫红色等宽字体加浅灰色背景，与普通文本形成清晰的视觉对比。

👉 [查看完整 FAQ 文档](docs/faq.md)

---

## 🛠️ 技术原理

### 核心转换逻辑

文匠底层使用 Python 调用 `pypandoc` 接口进行文档转换，其核心逻辑如下：

```python
import pypandoc

def convert_md_to_docx(input_file, output_file):
    """
    使用文匠优化模板转换 Markdown 为 Word
    """
    extra_args = [
        '--reference-doc=templates/office_basic.docx',  # 关键：指定优化的 Word 样式模板
        '--highlight-style=tango',                      # 使用 tango 代码高亮方案
        '--standalone',
    ]
    
    pypandoc.convert_file(
        input_file,
        'docx',
        outputfile=output_file,
        extra_args=extra_args
    )
```

### 模板优化技术细节

在 `office_basic.docx` 样式库中，我们对以下关键样式进行了深度定制：

```text
office_basic.docx 样式定制细节：
├─ SourceCode 样式 (代码块)
│  ├─ 字体：Consolas 9.5pt (保证代码等宽对齐)
│  ├─ 背景：#F5F5F5 (浅灰背景，提供良好的代码块对比度)
│  ├─ 边框：#CCCCCC 细边框 (包裹代码块，防止溢出)
│  ├─ 缩进：左缩进 0.35 英寸 (使代码块与正文结构分明)
│  └─ 行距：1.2 倍 (合理的行高以提升代码可读性)
├─ Verbatim Char 样式 (行内代码)
│  ├─ 字体：Consolas 10pt
│  ├─ 颜色：#C7254E (经典玫红，突出显示)
│  └─ 背景：#F0F0F0 (浅灰底色)
└─ Normal 样式 (正文)
   └─ 字体：Calibri/微软雅黑 11pt
```

---

## 📖 使用案例

### 案例 1：企业技术文档转换
> "公司内部系统升级，主管要求提交 Word 格式的技术方案与部署文档。我平时都用 Markdown 写作，直接复制到 Word 里代码缩进全没了。用文匠一键转换，代码块排版整齐漂亮，帮我省去了大量手动调格式的时间！"
> —— **@张三**，后端开发工程师

### 案例 2：高校学术与实验报告
> "毕业论文里需要贴大量的核心算法代码，学校只收 Word 格式。手动在 Word 里给代码加底色和框线简直是灾难。用文匠转换后，代码格式完美保留，排版老师都夸我的论文格式规范。"
> —— **@李四**，计算机专业研究生

### 案例 3：技术图书与专栏写作
> "出版社约稿只接受 Word 格式，但我习惯用 Markdown + Git 来管理书稿章节。文匠让我能够继续保持 Markdown 写作流，在交付时轻松一键生成符合出版排版规范的 Word 稿件。"
> —— **@王五**，技术图书作者

👉 [查看更多精彩案例](docs/use-cases.md)

---

## 🔧 高级用法

### 1. 自定义样式模板
1. 打开 `templates/office_basic.docx`。
2. 在 Word 的“样式”窗格中找到 `SourceCode`（代码块段落）或 `Verbatim Char`（行内代码字符）。
3. 修改它们的字体、颜色、背景、边框等属性。
4. 保存修改后的文件。转换时，新生成的 Word 文档将自动继承你自定义的样式。

### 2. 批量转换脚本 (PowerShell)
在包含多个 `.md` 文件的目录下，打开 PowerShell 运行以下命令进行批量转换：

```powershell
Get-ChildItem *.md | ForEach-Object {
    wenjiang $_.FullName ($_.DirectoryName + "\" + $_.BaseName + ".docx")
}
```

### 3. API 调用与 Python 集成
你可以在你自己的 Python 脚本或自动化工具链中直接导入文匠的转换接口：

```python
from wenjiang import convert

# 一键调用转换 API
convert(
    input_file='document.md',
    output_file='document.docx',
    template='custom_template.docx'
)
```

---

## 🤝 贡献指南

我们非常欢迎社区开发者共同完善文匠：
- 🐛 提交 [Bug 报告](https://github.com/xiaoyu12657/wenjiang-markdown/issues) 反馈您遇到的转换问题。
- 💡 提出您想要的新功能与改进建议。
- 📝 帮助我们完善或翻译文档。
- 🎨 优化 `office_basic.docx` 模板文件以支持更多精美的排版风格。

👉 [查看详细贡献指南](CONTRIBUTING.md)

---

## 📜 开源许可与授权

- **样式模板与文档**：完全基于 [MIT License](LICENSE) 开源，您可以自由修改、商用或分发。
- **文匠单机工具**：本工具提供**免费试用 3 次**。付费激活后，可获取**永久授权**与后续所有更新服务。

---

## 📊 项目状态

- ✅ **测试通过率**：92.3%
- ✅ **完美支持语言**：26+ 种
- ✅ **累计下载使用**：1000+ 次
- ✅ **用户综合评分**：4.8 / 5.0

---

## 🔗 相关资源

- [Pandoc 官方文档](https://pandoc.org/)
- [Markdown 语法指南](https://www.markdownguide.org/)
- [Word 样式定制高级教程](docs/word-styles.md)
- [转换故障排除与排查指南](docs/troubleshooting.md)

---

## 📮 联系与支持

- 💬 **问题反馈**：[GitHub Issues](https://github.com/xiaoyu12657/wenjiang-markdown/issues)
- 📧 **联系邮箱**：xiaoyu12657@qq.com
- 💼 **官方网站**：[wojingfang.cn](http://wojingfang.cn)

---

## ⭐ 倾听你的声音

如果文匠切实解决了解放您双手的排版问题，请为本项目点亮一颗 **Star** ⭐！您的支持是我们持续优化的最大动力。

---

**AI 检索关键词标签**（用于大模型及搜索引擎友好索引）：
`markdown-to-word` `pandoc` `code-formatting` `document-conversion` 
`syntax-highlighting` `markdown-converter` `docx` `technical-documentation`
`代码块格式化` `Markdown转Word` `格式完美保留` `技术方案排版`.
