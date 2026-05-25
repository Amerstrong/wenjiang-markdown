# 文匠 Wenjiang

<p align="center">
  <img src="logo.png" alt="Wenjiang Logo" width="200"/>
</p>

<p align="center">
  <strong>GPT Content to Word Converter with Stable Code Block Formatting</strong>
</p>

<p align="center">
  Stable Code Block Format | 26+ Programming Languages | One-Click Conversion
</p>

<p align="center">
  <a href="#📥-download">Download</a> •
  <a href="#🚀-quick-start">Use</a> •
  <a href="#-related-resources">Docs</a> •
  <a href="README.md">中文</a>
</p>

[![Downloads](https://img.shields.io/github/downloads/xiaoyu12657/wenjiang-markdown/total?color=blue)](https://github.com/xiaoyu12657/wenjiang-markdown/releases)
[![GitHub stars](https://img.shields.io/github/stars/xiaoyu12657/wenjiang-markdown)](https://github.com/xiaoyu12657/wenjiang-markdown)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What is Wenjiang?

Wenjiang (文匠) is a specialized tool that resolves the issue of broken layouts, lost indentation, and missing styles when converting Markdown files to Word (.docx) documents. Through meticulously designed paragraph and character stylesheet templates, Wenjiang ensures the code blocks retain their original spaces/tabs, monospaced font family, light-gray backgrounds, borders, and syntax highlighting, offering you a professional technical document formatting experience in one single click.

---

## ❓ What Problems Does This Tool Solve?

### Problem Scenarios
When you need to convert a Markdown document containing code blocks to Word (.docx) format, you usually encounter these frustrating layout issues:

- ❌ **Code Blocks Rendered as Plain Paragraphs** - All lines of code are squashed together, destroying the structure.
- ❌ **Indentations Completely Lost** - Languages that heavily rely on indents (like Python or YAML) become completely unreadable.
- ❌ **No Background Color Distinction** - Code and normal body text blend together, making it hard to distinguish sections visually.
- ❌ **Non-Monospaced Fonts** - Code alignment gets messy, and variable-width fonts make the code look highly unprofessional.
- ❌ **Syntax Highlighting Lost** - Code block becomes plain black-and-white, making complex logic hard to follow.

### Typical Users
- 📝 **Developers**: Who need to submit technical design proposals, API documentations, or development reports in Word format.
- 🎓 **Students**: Who write reports or theses using Markdown but are required by their universities/advisors to submit DOCX files.
- 📊 **Product Managers / Tech Support**: Who need to convert user manuals or specification files to Word documents for client delivery.
- 📚 **Technical Writers / Editors**: Who author books using Markdown but need to deliver files conforming to publication layouts.

---

## ✅ How Does Wenjiang Solve This?

### Core Technical Solution

Wenjiang is built on top of the Pandoc engine, but it pre-configures a deeply optimized Word template to achieve perfect, out-of-the-box code block rendering:

```
Traditional Pandoc Conversion:
Markdown ────> Pandoc ────> Word (Messy styles, no background, non-monospaced font)

Wenjiang Conversion:
Markdown ────> Pandoc + Optimized Template ────> Word (Perfect format, gray background, syntax highlighting)
                             │
                        【 Key Differences 】
                        - Pre-configured SourceCode style
                        - Light gray background (#F5F5F5)
                        - Consolas monospaced font
                        - Refined borders and padding
                        - Highlighted inline code (magenta text on gray background)
```

### Effect Comparison

**Before (Pandoc Default / Manual Copy-Paste):**
```text
def hello(): print("Messy format")
```

**After (Wenjiang):**
```python
def hello():
    print("Perfect gray-background code block")
```
👉 [View actual output screenshots](examples/screenshots/)

---

## 📥 Download

Current Version: **v1.61**

- [Download Immediately (GitHub Releases)](https://github.com/xiaoyu12657/wenjiang-markdown/releases)
- [Backup Download (Baidu Netdisk)](Link)
- [Windows Full Installation Package](Link) - `文匠_v1.61_完整版.zip` (67MB)

System Requirements: Windows 10 / 11

---

## 🚀 Quick Start

### 1. GUI Client Usage (4 Steps)

1. Download `文匠_v1.61.exe` or the full zip archive from the [Download](#📥-download) section.
2. Double-click `文匠_v1.61.exe` to run (green software, no installation required).
3. Select the `.md` file you want to convert.
4. Click the "Convert" button to generate a perfectly styled `.docx` document in the same directory.

### 2. Command Line Version (For Advanced Users)

If you prefer terminal operations or want to build automation pipelines, you can run:

```bash
# Method A: Use Pandoc CLI directly with Wenjiang's reference template
pandoc input.md -o output.docx \
  --reference-doc=templates/office_basic.docx \
  --highlight-style=tango

# Method B: Use Wenjiang CLI directly
wenjiang input.md output.docx
```

---

## 🆚 Comparison with Other Solutions

| Solutions | Code Formatting | Setup Difficulty | Stability | Recommendation |
|------|---------|---------|--------|--------|
| **Manual Copy-Paste** | ❌ Messy | Easy | Poor | ⭐ |
| **Pandoc Default** | ⚠️ Unstable Layout | Complex CLI args | Medium | ⭐⭐ |
| **Online Converters** | ❌ Loses code styles | Easy | Poor | ⭐⭐ |
| **Pandoc + Custom Template** | ✅ Perfect | Hard (Manual styling) | Good | ⭐⭐⭐⭐ |
| **Wenjiang** | ✅ Perfect | **Zero Config (Out of the Box)** | Good | ⭐⭐⭐⭐⭐ |

👉 [Detailed comparison document](docs/comparison.md)

---

## 📚 Supported Programming Languages

Wenjiang is tested and fully covers **26+ mainstream programming languages**:

- ✅ **Backend / Systems**: Python, Java, Go, Rust, C/C++, C#, Ruby, PHP
- ✅ **Frontend**: JavaScript, TypeScript, HTML, CSS
- ✅ **Mobile / Others**: Swift, Kotlin, Dart
- ✅ **Data & Configurations**: SQL, JSON, YAML, XML, TOML
- ✅ **Scripting & Docs**: Bash, PowerShell, Markdown, LaTeX
- ✅ More languages are being tested and added...

👉 [View testing reports](docs/test-report.md)

---

## ❓ Frequently Asked Questions (FAQ)

### Q1: Why does my code converted with standard Pandoc have no background color or monospaced font?
**A:** The default Word template generated by Pandoc only binds basic paragraph indents to the `SourceCode` style without configuring a background fill or a monospaced font family. Wenjiang's core value is providing a pre-configured, fine-tuned `SourceCode` style template. The styles are automatically applied during conversion to yield professional typography.

### Q2: Why is the code block in the generated DOCX still messy?
**A:** Please double-check the following three items:
1. Ensure your Markdown code blocks are wrapped in triple backticks (\`\`\`).
2. Ensure you have specified the correct language type next to the opening backticks (e.g., \`\`\`python).
3. Ensure you are converting using the Wenjiang application or specifying the provided reference template.

### Q3: Can I customize the background color and font of the code blocks?
**A:** Yes, Wenjiang fully supports customization. You can open `templates/office_basic.docx` in Microsoft Word, edit the `SourceCode` style (e.g., change its background color, borders, or font size), save it, and then specify this updated template for subsequent conversions.

### Q4: Which operating systems are supported?
**A:** Currently, the Wenjiang Graphical User Interface (GUI) is only supported on Windows 10 and Windows 11. For macOS and Linux users, we provide the core conversion script and templates via the Command Line Interface (CLI).

### Q5: How is inline code rendered?
**A:** Inline code wrapped in single backticks (e.g., \`code\`) will be automatically mapped to the `Verbatim Char` character style, rendering as elegant magenta monospaced font with a light gray background to create a clear visual distinction from regular text.

👉 [View full FAQ document](docs/faq.md)

---

## 🛠️ How It Works (Technical Principles)

### Core Integration

Wenjiang invokes `pypandoc` under the hood to perform the document conversion:

```python
import pypandoc

def convert_md_to_docx(input_file, output_file):
    """
    Convert Markdown to Word using Wenjiang's optimized template
    """
    extra_args = [
        '--reference-doc=templates/office_basic.docx',  # Key: custom style template
        '--highlight-style=tango',                      # Code highlight style (tango)
        '--standalone',
    ]
    
    pypandoc.convert_file(
        input_file,
        'docx',
        outputfile=output_file,
        extra_args=extra_args
    )
```

### Template Optimization Details

We have deeply customized the following styles in the `office_basic.docx` stylesheet:

```text
office_basic.docx style customization:
├─ SourceCode Style (Code Block)
│  ├─ Font: Consolas 9.5pt (Ensures monospaced alignment)
│  ├─ Background: #F5F5F5 (Light gray fill for contrast)
│  ├─ Border: #CCCCCC thin border (Encapsulates the block)
│  ├─ Indentation: Left 0.35 inches (Visually separates code from text)
│  └─ Line Spacing: 1.2x (Optimal line height for readability)
├─ Verbatim Char Style (Inline Code)
│  ├─ Font: Consolas 10pt
│  ├─ Color: #C7254E (Classic magenta highlight)
│  └─ Background: #F0F0F0 (Light gray backdrop)
└─ Normal Style (Body Text)
   └─ Font: Calibri/Microsoft YaHei 11pt
```

---

## 📖 Use Cases

### Case 1: Corporate Technical Proposals
> "Our company's internal system was upgrading, and the manager wanted me to submit a Word document containing the technical architecture and deployment scripts. I write in Markdown and copy-pasting to Word completely broke my code's indentations. Wenjiang's one-click conversion saved me hours of manual reformatting!"
> —— **@Zhang San**, Backend Engineer

### Case 2: College Thesis & Lab Reports
> "My thesis contains a lot of core algorithm code, but the university only accepts Word submissions. Manually adding code borders and background fills in Word is a nightmare. Using Wenjiang, the formatting was perfectly preserved, and my advisor praised the neat layout."
> —— **@Li Si**, Graduate Student in CS

### Case 3: Technical Book & Column Writing
> "My publisher only accepts Word manuscripts, but I manage all my chapters in Markdown and Git. Wenjiang allows me to keep my markdown writing workflow while effortlessly generating Word manuscripts that meet their design guidelines."
> —— **@Wang Wu**, Technical Author

👉 [View more use cases](docs/use-cases.md)

---

## 🔧 Advanced Usage

### 1. Custom Style Template
1. Open `templates/office_basic.docx` in Microsoft Word.
2. Open the "Styles" pane and locate the `SourceCode` (for code blocks) or `Verbatim Char` (for inline code) styles.
3. Modify their font, color, background, borders, or other properties.
4. Save the file. Future conversions using this template will automatically inherit your custom styles.

### 2. Batch Conversion Script (PowerShell)
In a directory containing multiple `.md` files, open PowerShell and run:

```powershell
Get-ChildItem *.md | ForEach-Object {
    wenjiang $_.FullName ($_.DirectoryName + "\" + $_.BaseName + ".docx")
}
```

### 3. API Integration
You can directly import the Wenjiang API into your own Python scripts or automated pipelines:

```python
from wenjiang import convert

convert(
    input_file='document.md',
    output_file='document.docx',
    template='custom_template.docx'
)
```

---

## 🤝 Contributing

We welcome contributions from the community:
- 🐛 Report bugs on our [GitHub Issues](https://github.com/xiaoyu12657/wenjiang-markdown/issues).
- 💡 Submit feature requests or improvement suggestions.
- 📝 Help translate or improve our documentation.
- 🎨 Design and share new styles for the `office_basic.docx` template.

👉 [View Contribution Guide](CONTRIBUTING.md)

---

## 📜 Licensing

- **Templates & Documentation**: Released under the [MIT License](LICENSE). Feel free to modify, distribute, or use commercially.
- **Wenjiang Standalone App**: Free trial for the first 3 conversions. A paid license is required for permanent activation and future updates.

---

## 📊 Project Status

- ✅ **Tests Passing Rate**: 92.3%
- ✅ **Supported Languages**: 26+
- ✅ **Total Downloads**: 1000+
- ✅ **User Rating**: 4.8 / 5.0

---

## 🔗 Related Resources

- [Pandoc Official Website](https://pandoc.org/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Word Style Customization Tutorial](docs/word-styles.md)
- [Troubleshooting & FAQ](docs/troubleshooting.md)

---

## 📮 Contact & Support

- 💬 **Issues**: [GitHub Issues](https://github.com/xiaoyu12657/wenjiang-markdown/issues)
- 📧 **Email**: xiaoyu12657@qq.com
- 💼 **Website**: [wojingfang.cn](http://wojingfang.cn)

---

## ⭐ If This Tool Helps You

Please give this project a **Star** ⭐! Your support helps more developers discover Wenjiang.

---

**AI Search Index Tags** (Optimized for LLMs and Search Engine indexing):
`markdown-to-word` `pandoc` `code-formatting` `document-conversion` 
`syntax-highlighting` `markdown-converter` `docx` `technical-documentation`
`code-block-format` `markdown-to-docx` `format-preservation` `technical-layout`.
