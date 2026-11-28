---
---
name: site-ops
description: 个人官网的页面美化、前端样式调整、文章新增、本地构建校验与 Git 部署规范。修改网页 UI、新增或更新文章、调整构建脚本或准备发布上线时必须调用。
---

# 执行规范
## 1. 源码与产物隔离（红线）
- **严禁直接修改生成的 `.html` 产物文件**（或 `dist/`、`public/` 等输出目录）。
- 所有修改必须落在源文件上：
  - 文章内容：`content/posts/` 下的 `.md` 文件
  - 页面结构与美化：模板文件（如 `templates/`）及样式/脚本文件（如 `static/`、`assets/`）
  - 构建逻辑：`build.py`

## 2. 文件命名与 Frontmatter 规范
- 新增文章统一使用**纯英文小写 + 短横线**命名（例如 `tool-update-guide.md`），禁止使用中文文件名，防止路径冲突或路由解析失败。
- 修改或新增 Markdown 文章后，必须对照 `build.py` 的解析逻辑，逐项核对 Frontmatter 字段（如 `title`、`date`、`description`、`related_tool` 等）的键名、引号和格式，确保不会被构建脚本静默跳过。

## 3. 编码与换行符防错规范（防 Windows CRLF 报错）
- 新建或修改任何 `.md`、`.py`、`.html`、`.css`、`.js` 文件时，必须使用 **UTF-8（无 BOM）+ LF（`\n`）换行符**保存。
- 修改或审查 `build.py` 时，必须确保满足以下防错机制：
  1. 读取文件后第一时间归一化换行符：`text = raw_text.replace("\r\n", "\n").replace("\r", "\n")`。
  2. 拆分 Frontmatter 或逐行解析时，使用 `splitlines()` 替代 `split("\n")`，并在匹配 `---` 或字段值前执行 `.strip()`。
  3. 写入产物文件时显式指定 `encoding="utf-8", newline="\n"`。

## 4. 页面美化与前端改造标准
- **响应式优先：** 每次调整 CSS 或布局，必须同时兼顾桌面端（1280px+）与移动端（375px），严禁出现横向滚动条、文字截断或按钮错位。
- **轻量简洁：** 优先使用原生 CSS 变量、Flex/Grid 布局和轻量交互，不擅自引入重型前端框架或外部慢速 CDN。
- **保护核心转化路径：** 美化改版时，不得破坏现有的工具展示卡片、下载链接、文章跳转和导航结构。

## 5. 构建校验与部署闭环
1. 任何代码或文章改动完成后，**必须在终端执行本地构建命令**（如 `python3 build.py`）。
2. 检查构建输出：
   - 终端必须 0 报错退出。
   - 核对生成的文章/页面数量与源文件一致，没有漏生成或误删页面。
3. 运行 `git status` 与 `git diff --stat` 检查变更范围，确认没有把临时文件或垃圾文件纳入提交。
4. 仅在本地构建和检查全部通过后，才允许执行 `git add`、`git commit` 与 `git push`（若托管平台如 Cloudflare Pages 依赖构建命令，切勿改动导致构建命令为空）。
一、 网站构建与部署最容易出错的 3 条规矩
1. 只改源文件，严禁直接修改构建产物
常见翻车： AI 为了省事，直接去改生成的 .html 页面或 dist/、public/ 目录。结果下次一跑构建脚本，改动全被覆盖，或者源码和线上页面彻底不同步。

硬性规矩： 新增文章或改版样式时，只允许修改源目录（如 content/posts/、templates/、static/）。所有最终 HTML 必须由构建脚本重新生成。

2. 强制核对构建命令、文件名与 Frontmatter 规范
常见翻车：

托管平台（如 Cloudflare Pages）的 Build command 留空，导致“0 秒假部署”，页面压根没更新。

新文章用了中文文件名或与已有文件冲突，或者 Frontmatter 里的必填字段（如 title、date、related_tool）格式写错，导致脚本直接跳过该文章。

硬性规矩：

部署配置必须明确写出构建命令（如 python3 build.py）。

文章文件名统一使用纯英文小写 + 短横线（如 my-post-guide.md）。

写完 Markdown 后，必须逐项对照构建脚本的字段要求检查 Frontmatter。

3. 本地构建校验通过后，才允许 git push
常见翻车： AI 改完代码直接提交推送，线上构建失败或者页面排版错乱，只能反复提交“fix”补丁。

硬性规矩： 推送前必须在本地终端跑完构建命令，并确认两件事：终端无报错、生成的文章列表数量与预期一致，验证通过后再执行 git add / commit / push。

二、 换行编译出错的改进内容
Windows 默认使用 CRLF（\r\n），而 Linux 云端构建环境及多数正则解析器默认按 LF（\n）处理。这会导致 Frontmatter 的 --- 分隔符匹配失败、Shell 脚本报 ^M 错误或 Markdown 段落/代码块解析错乱。

改进方案从脚本、Git 仓库、解析逻辑三层同时堵死：

构建脚本读取时强制统一换行符（最直接）

在 build.py 读取 Markdown 或模板文件后，第一时间做归一化处理：

Python


text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
写入生成的 HTML 文件时，显式指定编码和换行符：

Python


with open(output_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(html_content)
解析逻辑弃用硬编码 \n 切割

拆分 Frontmatter 或逐行解析时，用 text.splitlines() 替代 text.split("\n")。

匹配字段值（如 ---、key: value）前先执行 .strip()，防止行尾残留的 \r 或空格导致匹配失效。

在仓库根目录加 .gitattributes 锁定 LF（防复发）

新建 .gitattributes 文件并提交，强制所有源码、文章和脚本在 Git 层面统一为 LF：

Plaintext


* text=auto eol=lf
*.md text eol=lf
*.py text eol=lf
*.html text eol=lf
*.css text eol=lf
*.js text eol=lf
编辑器与 AI 写入约束

在 SKILL.md 中明确要求：AI 新建或修改任何 .md、.py、.sh 文件时，必须使用 UTF-8（无 BOM）+ LF 换行符保存。
## 1. 修改原则
- 仅修改源目录（如 `content/`、`templates/` 或 `src/`），**严禁直接修改构建产物目录的 HTML**。
- 改完样式或文案后，必须先运行本地构建命令验证无报错。

## 2. 构建与校验步骤
1. 在终端执行构建脚本（例如 `python3 build.py` 或 `npm run build`）。
2. 检查输出日志，确认没有 Frontmatter 解析错误或缺失文件。
3. 启动本地预览并检查页面布局，确认无错位后再执行 `git add / commit / push`。

## 3. 禁止事项
- 不要在未通过本地构建的情况下直接推送代码。