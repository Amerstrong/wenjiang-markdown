#!/usr/bin/env python3
"""Build the AI Explorer Laboratory static site using only the Python stdlib."""

from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
TOOLS_DIR = CONTENT_DIR / "tools"
POSTS_DIR = CONTENT_DIR / "posts"
SITE_URL = "https://wojingfang.cn"
SITE_NAME = "AI探索者实验室"
SITE_AUTHOR = "AI探索者"
CONTACT_EMAIL = "xiaoyu12657@qq.com"


@dataclass(slots=True)
class Document:
    source: Path
    meta: dict[str, Any]
    body: str

    @property
    def slug(self) -> str:
        return str(self.meta.get("slug") or self.source.stem)

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.slug)


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in inner.split(",")]
    return value


def parse_frontmatter(text: str, source: Path) -> Document:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError(f"{source}: Markdown 必须包含 Frontmatter")
    try:
        _, metadata, body = normalized.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"{source}: Frontmatter 未正确闭合") from exc

    result: dict[str, Any] = {}
    active_key = ""
    for raw_line in metadata.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("  - ", "- ")) and active_key:
            if not isinstance(result.get(active_key), list):
                result[active_key] = []
            result[active_key].append(parse_scalar(line.lstrip()[1:].strip()))
            continue
        if ":" not in line:
            raise ValueError(f"{source}: 无法解析 Frontmatter 行: {line}")
        key, raw_value = line.split(":", 1)
        active_key = key.strip()
        value = raw_value.strip()
        result[active_key] = [] if not value else parse_scalar(value)

    return Document(source=source, meta=result, body=body.strip())


def load_documents(folder: Path) -> list[Document]:
    documents: list[Document] = []
    for source in sorted(folder.glob("*.md")):
        documents.append(parse_frontmatter(source.read_text(encoding="utf-8-sig"), source))
    return documents


def text_value(meta: dict[str, Any], key: str, default: str = "") -> str:
    value = meta.get(key, default)
    return str(value).strip() if value is not None else default


def text_list(meta: dict[str, Any], key: str) -> list[str]:
    value = meta.get(key, [])
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def bool_value(meta: dict[str, Any], key: str, default: bool = False) -> bool:
    value = meta.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def heading_id(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[`*_~\[\](){}:：,，。.!！?？/\\|]+", "", value)
    value = re.sub(r"\s+", "-", value.strip())
    return value or "section"


def inline_markdown(value: str) -> str:
    rendered = html.escape(value, quote=False)

    def image(match: re.Match[str]) -> str:
        alt = match.group(1)
        src = match.group(2)
        title = match.group(3) or alt
        return (
            f'<img src="{html.escape(src, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}" title="{html.escape(title, quote=True)}" loading="lazy">'
        )

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = match.group(2)
        external = url.startswith(("http://", "https://"))
        extra = ' target="_blank" rel="noopener noreferrer"' if external else ""
        return f'<a href="{html.escape(url, quote=True)}"{extra}>{label}</a>'

    rendered = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)", image, rendered)
    rendered = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, rendered)
    rendered = re.sub(r"`([^`]+)`", r"<code>\1</code>", rendered)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", rendered)
    return rendered


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def render_markdown(markdown_text: str) -> str:
    lines = markdown_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    result: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            language_class = f' class="language-{html.escape(language, quote=True)}"' if language else ""
            code = html.escape("\n".join(code_lines))
            result.append(f"<pre><code{language_class}>{code}</code></pre>")
            continue

        if stripped.startswith("<") and not stripped.startswith("<http"):
            html_lines: list[str] = []
            while index < len(lines) and lines[index].strip():
                html_lines.append(lines[index])
                index += 1
            result.append("\n".join(html_lines))
            continue

        if stripped.startswith("### "):
            title = stripped[4:].strip()
            result.append(f'<h3 id="{heading_id(title)}">{inline_markdown(title)}</h3>')
            index += 1
            continue
        if stripped.startswith("## "):
            title = stripped[3:].strip()
            result.append(f'<h2 id="{heading_id(title)}">{inline_markdown(title)}</h2>')
            index += 1
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            result.append(f'<h2 id="{heading_id(title)}">{inline_markdown(title)}</h2>')
            index += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            result.append("<hr>")
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            headers = [cell.strip() for cell in stripped.strip("|").split("|")]
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            table = ['<div class="table-scroll"><table>', "<thead><tr>"]
            table.extend(f"<th>{inline_markdown(cell)}</th>" for cell in headers)
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>")
                table.extend(f"<td>{inline_markdown(cell)}</td>" for cell in row)
                table.append("</tr>")
            table.append("</tbody></table></div>")
            result.append("".join(table))
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip()[1:].strip())
                index += 1
            result.append(f"<blockquote><p>{inline_markdown(' '.join(quote_lines))}</p></blockquote>")
            continue

        unordered = re.match(r"^[-*+]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if unordered or ordered:
            ordered_list = bool(ordered)
            tag = "ol" if ordered_list else "ul"
            items: list[str] = []
            pattern = r"^\d+[.)]\s+(.+)$" if ordered_list else r"^[-*+]\s+(.+)$"
            while index < len(lines):
                candidate = re.match(pattern, lines[index].strip())
                if not candidate:
                    break
                items.append(f"<li>{inline_markdown(candidate.group(1))}</li>")
                index += 1
            result.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            candidate = lines[index].strip()
            if not candidate:
                break
            if (
                candidate.startswith(("#", "```", ">", "|", "<"))
                or re.match(r"^[-*+]\s+", candidate)
                or re.match(r"^\d+[.)]\s+", candidate)
            ):
                break
            paragraph_lines.append(candidate)
            index += 1
        result.append(f"<p>{inline_markdown(' '.join(paragraph_lines))}</p>")

    return "\n".join(result)


def canonical_for(route: str) -> str:
    if route == "":
        return f"{SITE_URL}/"
    return f"{SITE_URL}/{route.lstrip('/')}"


def absolute_asset(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    return f"{SITE_URL}/{path.lstrip('/')}"


def brand_mark() -> str:
    return """
<svg viewBox="0 0 32 32" aria-hidden="true">
  <path d="M7 9.5 16 4l9 5.5v10L16 25l-9-5.5z" fill="none" stroke="white" stroke-width="1.8"/>
  <circle cx="16" cy="14.5" r="3.2" fill="#ff8a62"/>
  <path d="M10.5 19.2 16 22l5.5-2.8M16 17.7V22" fill="none" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
</svg>""".strip()


def header_html(active: str) -> str:
    links = [
        ("home", "/", "首页"),
        ("tools", "/tools/", "工具库"),
        ("posts", "/posts/", "技术专栏"),
        ("about", "/about.html", "关于AI探索者"),
    ]
    items = "\n".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
        for key, href, label in links
    )
    return f"""
<a class="skip-link" href="#main">跳到正文</a>
<header class="site-header">
  <div class="nav-shell">
    <a class="brand" href="/" aria-label="{SITE_NAME}首页">
      <span class="brand-mark">{brand_mark()}</span>
      <span class="brand-copy"><strong>AI探索者</strong><small>EXPLORER LAB</small></span>
    </a>
    <nav class="site-nav" aria-label="主导航">
      {items}
    </nav>
  </div>
</header>
"""


def footer_html() -> str:
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <a class="brand" href="/">
        <span class="brand-mark">{brand_mark()}</span>
        <span class="brand-copy"><strong>AI探索者实验室</strong><small>LOCAL · EDGE · OPEN</small></span>
      </a>
      <p>记录本地离线 AI、跨设备工具、边缘硬件与自动化脚本的实战过程。</p>
    </div>
    <div class="footer-links">
      <strong>探索</strong>
      <a href="/tools/">工具库</a>
      <a href="/posts/">技术专栏</a>
      <a href="/about.html">关于AI探索者</a>
    </div>
    <div class="footer-links">
      <strong>索引与联系</strong>
      <a href="/sitemap.xml">Sitemap</a>
      <a href="/llms.txt">llms.txt</a>
      <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
    </div>
  </div>
  <div class="footer-copy">© 2026 {SITE_NAME} · 本站使用无 CDN 的静态 HTML 构建 · woJingFang.cn</div>
</footer>
"""


def page_html(
    *,
    route: str,
    title: str,
    description: str,
    keywords: str,
    content: str,
    active: str,
    schema: dict[str, Any],
    image: str = "/favicon_io/android-chrome-512x512.png",
    page_type: str = "website",
) -> str:
    canonical = canonical_for(route)
    styles = (ROOT / "site.css").read_text(encoding="utf-8")
    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    og_image = absolute_asset(image)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="keywords" content="{html.escape(keywords, quote=True)}">
  <meta name="author" content="{SITE_AUTHOR}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon_io/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon_io/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/favicon_io/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#0d6b55">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="{page_type}">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title, quote=True)}">
  <meta name="twitter:description" content="{html.escape(description, quote=True)}">
  <meta name="twitter:image" content="{og_image}">
  <script type="application/ld+json">{schema_json}</script>
  <style>
{styles}
  </style>
</head>
<body>
{header_html(active)}
<main id="main">
{content}
</main>
{footer_html()}
</body>
</html>
"""


def tag_html(label: str, warm: bool = False) -> str:
    class_name = "tag warm" if warm else "tag"
    return f'<span class="{class_name}">{html.escape(label)}</span>'


def tool_cover(tool: Document, large: bool = False) -> str:
    cover = text_value(tool.meta, "cover")
    alt = text_value(tool.meta, "cover_alt", text_value(tool.meta, "name", tool.title))
    if cover:
        return (
            f'<div class="tool-cover"><span class="cover-badge">'
            f'{html.escape(text_value(tool.meta, "category", "工具"))}</span>'
            f'<img src="{html.escape(cover, quote=True)}" alt="{html.escape(alt, quote=True)}"'
            f' loading="{"eager" if large else "lazy"}"></div>'
        )
    return f"""
<div class="tool-cover cover-filebeam">
  <span class="cover-badge">LOCAL TRANSFER</span>
  <div class="signal-map" aria-label="电脑与手机在同一局域网内直接互传文件">
    <div class="signal-device"><strong>PC</strong>浏览器上传</div>
    <div class="signal-link">⇄</div>
    <div class="signal-device"><strong>PHONE</strong>扫码即用</div>
  </div>
</div>""".strip()


def tool_card(tool: Document) -> str:
    tags = text_list(tool.meta, "features")[:2]
    return f"""
<article class="tool-card">
  {tool_cover(tool)}
  <div class="tool-body">
    <div class="tag-row">
      {''.join(tag_html(item) for item in tags)}
      {tag_html(text_value(tool.meta, "price_label", "查看详情"), warm=True)}
    </div>
    <h3><a href="/tools/{tool.slug}.html">{html.escape(text_value(tool.meta, "name", tool.title))}</a></h3>
    <p>{html.escape(text_value(tool.meta, "summary"))}</p>
    <div class="tool-meta">
      <span>{html.escape(text_value(tool.meta, "platform", "跨平台"))}</span>
      <a href="/tools/{tool.slug}.html">查看详情 →</a>
    </div>
  </div>
</article>"""


def post_date(post: Document) -> str:
    return text_value(post.meta, "date", "2026-01-01")


def post_card(post: Document) -> str:
    tags = [text_value(post.meta, "category", "技术"), *text_list(post.meta, "tags")[:2]]
    return f"""
<article class="post-card">
  <div class="tag-row">{''.join(tag_html(item) for item in tags if item)}</div>
  <time datetime="{html.escape(post_date(post))}">{html.escape(post_date(post))}</time>
  <h3><a href="/posts/{post.slug}.html">{html.escape(post.title)}</a></h3>
  <p>{html.escape(text_value(post.meta, "summary"))}</p>
  <div class="post-footer">
    <span>{html.escape(text_value(post.meta, "category", "技术专栏"))}</span>
    <a href="/posts/{post.slug}.html">阅读全文 →</a>
  </div>
</article>"""


def build_home(tools: list[Document], posts: list[Document]) -> str:
    featured_tools = [tool for tool in tools if bool_value(tool.meta, "featured", True)][:3]
    latest_posts = sorted(posts, key=post_date, reverse=True)[:3]
    content = f"""
<div class="page-shell">
  <section class="hero" aria-labelledby="home-title">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">LOCAL-FIRST · EDGE AI · OPEN TOOLS</span>
        <h1 id="home-title">AI 探索者 <span class="accent">·</span><br>AI 与实用工具解决真实生活中的小麻烦</h1>
        <p class="lead">专注本地离线 AI 应用、跨设备效率工具（FileBeam / 文匠）与自动化脚本实战。本地大模型、边缘硬件（Jetson/树莓派）与极简桌面效率工具。所有自研免费/开源软件与实战踩坑记录均在此归档。</p>
        <div class="hero-actions">
          <a class="button accent" href="/tools/">进入工具库 <span aria-hidden="true">→</span></a>
          <a class="button light" href="/posts/">阅读技术专栏</a>
        </div>
        <div class="hero-stats" aria-label="网站方向">
          <div class="hero-stat"><strong>LOCAL</strong><span>离线运行，数据留在本机</span></div>
          <div class="hero-stat"><strong>EDGE</strong><span>Jetson / 树莓派实验</span></div>
          <div class="hero-stat"><strong>OPEN</strong><span>免费开源与公开记录</span></div>
        </div>
      </div>
      <aside class="hero-terminal" aria-label="AI探索者实验室工作方式">
        <div class="terminal-bar">
          <span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-dot"></span>
          <span class="terminal-title">explorer_lab.log</span>
        </div>
        <div class="terminal-body">
          <p class="terminal-line"><span class="prompt">$</span> find problem --real-life</p>
          <p class="terminal-line"><span class="ok">✓</span> 识别高频小麻烦</p>
          <p class="terminal-line"><span class="ok">✓</span> 优先本地与离线方案</p>
          <p class="terminal-line"><span class="ok">✓</span> 做成可复用的工具</p>
          <p class="terminal-line"><span class="ok">✓</span> 测试、发布、公开踩坑</p>
          <div class="signal-map">
            <div class="signal-device"><strong>IDEA</strong>真实需求</div>
            <div class="signal-link">→</div>
            <div class="signal-device"><strong>TOOL</strong>可用软件</div>
          </div>
        </div>
      </aside>
    </div>
  </section>

  <section class="section" aria-labelledby="problems-title">
    <div class="section-head">
      <div><span class="section-kicker">WHAT I EXPLORE</span><h2 id="problems-title">从真实麻烦出发，不做炫技演示</h2></div>
      <p>优先解决每天会遇到、但现有工具又不够顺手的问题，并把构建过程完整记录下来。</p>
    </div>
    <div class="topic-grid">
      <article class="topic-card">
        <span class="topic-index">01 / LOCAL AI</span>
        <h3>本地大模型与离线应用</h3>
        <p>围绕隐私、可离线运行和低依赖部署，探索本地文档处理、推理服务与桌面 AI 工具。</p>
      </article>
      <article class="topic-card">
        <span class="topic-index">02 / CROSS-DEVICE</span>
        <h3>跨设备与局域网效率</h3>
        <p>让手机、电脑和边缘设备在同一网络内直接协作，减少登录、上传和云端中转。</p>
      </article>
      <article class="topic-card">
        <span class="topic-index">03 / AUTOMATION</span>
        <h3>自动化脚本与工程发布</h3>
        <p>把一次性的手工流程做成可测试、可复现、可发布的软件工程，而不是躺在硬盘里的脚本。</p>
      </article>
    </div>
  </section>

  <section class="section" aria-labelledby="tools-title">
    <div class="section-head">
      <div><span class="section-kicker">TOOL LIBRARY</span><h2 id="tools-title">已经做出来的工具</h2></div>
      <a class="button outline small" href="/tools/">查看全部工具</a>
    </div>
    <div class="tool-grid">{''.join(tool_card(tool) for tool in featured_tools)}</div>
  </section>

  <section class="section" aria-labelledby="posts-title">
    <div class="section-head">
      <div><span class="section-kicker">FIELD NOTES</span><h2 id="posts-title">技术专栏 · 实战踩坑记录</h2></div>
      <a class="button outline small" href="/posts/">查看全部文章</a>
    </div>
    <div class="post-grid">{''.join(post_card(post) for post in latest_posts)}</div>
  </section>

  <section class="section" id="about">
    <div class="home-band">
      <div class="home-band-grid">
        <div>
          <h2>一个持续做工具、记过程的 AI 探索者</h2>
          <p>关注本地优先、数据可控和真正能省时间的软件。这里不只展示成品，也记录需求判断、工程取舍、失败路径与可复现的解决方法。</p>
        </div>
        <a class="button light" href="/about.html">关于AI探索者 →</a>
      </div>
    </div>
  </section>
</div>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "alternateName": "AI 探索者实验室",
        "url": f"{SITE_URL}/",
        "description": "专注本地离线 AI 应用、跨设备效率工具与自动化脚本实战的个人品牌官网。",
        "inLanguage": "zh-CN",
        "publisher": {
            "@type": "Person",
            "name": SITE_AUTHOR,
            "email": CONTACT_EMAIL,
            "url": f"{SITE_URL}/about.html",
        },
    }
    return page_html(
        route="",
        title="AI探索者实验室｜AI与实用工具解决真实生活中的小麻烦",
        description="AI探索者实验室专注本地离线AI、跨设备效率工具、Jetson与树莓派边缘实践、自动化脚本和免费开源软件，归档FileBeam、文匠及真实工程踩坑记录。",
        keywords="AI探索者,本地离线AI,FileBeam,文匠,Wenjiang,Jetson,树莓派,跨设备文件传输,Markdown转Word,自动化脚本,免费开源工具",
        content=content,
        active="home",
        schema=schema,
    )


def build_tools_index(tools: list[Document]) -> str:
    cards = "".join(tool_card(tool) for tool in tools)
    content = f"""
<div class="page-shell">
  <header class="page-heading">
    <span class="section-kicker">TOOL LIBRARY</span>
    <h1>工具库：每一个工具都来自具体麻烦</h1>
    <p>这里的软件优先本地运行、低依赖、可解释。免费开源工具直接下载；需要授权维护的商业工具会清楚标注试用、价格与激活方式。</p>
  </header>
  <section class="section" aria-label="全部工具">
    <div class="tool-grid">{cards}</div>
  </section>
</div>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "AI探索者实验室工具库",
        "url": f"{SITE_URL}/tools/",
        "description": "收录FileBeam Lite、文匠 Markdown_Office等本地优先、跨设备与效率类软件。",
        "inLanguage": "zh-CN",
        "hasPart": [
            {"@type": "SoftwareApplication", "name": text_value(tool.meta, "name", tool.title), "url": f"{SITE_URL}/tools/{tool.slug}.html"}
            for tool in tools
        ],
    }
    return page_html(
        route="tools/",
        title="工具库｜AI探索者实验室",
        description="AI探索者实验室工具库：FileBeam Lite免费局域网文件互传、文匠Markdown_Office离线Markdown转Word，以及持续增加的本地效率工具。",
        keywords="AI工具库,FileBeam Lite,文匠 Markdown_Office,离线工具,局域网互传,Markdown转Word,免费开源软件",
        content=content,
        active="tools",
        schema=schema,
    )


def tool_schema(tool: Document) -> dict[str, Any]:
    is_free = bool_value(tool.meta, "is_free", False)
    offers: list[dict[str, Any]] = [
        {
            "@type": "Offer",
            "name": "免费使用",
            "price": "0",
            "priceCurrency": "CNY",
            "availability": "https://schema.org/InStock",
        }
    ]
    try:
        paid_price = float(text_value(tool.meta, "price", "0"))
    except ValueError:
        paid_price = 0
    if paid_price > 0:
        offers.append(
            {
                "@type": "Offer",
                "name": text_value(tool.meta, "price_label", "授权版"),
                "price": f"{paid_price:g}",
                "priceCurrency": "CNY",
                "url": text_value(tool.meta, "purchase_url", canonical_for(f"tools/{tool.slug}.html")),
            }
        )
    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": text_value(tool.meta, "name", tool.title),
        "description": text_value(tool.meta, "summary", tool.title),
        "applicationCategory": text_value(tool.meta, "category", "UtilitiesApplication"),
        "operatingSystem": text_value(tool.meta, "platform", "Windows"),
        "softwareVersion": text_value(tool.meta, "version"),
        "downloadUrl": text_value(tool.meta, "download_url", canonical_for(f"tools/{tool.slug}.html")),
        "url": canonical_for(f"tools/{tool.slug}.html"),
        "inLanguage": "zh-CN",
        "isAccessibleForFree": is_free,
        "offers": offers,
        "author": {"@type": "Person", "name": SITE_AUTHOR, "url": f"{SITE_URL}/about.html"},
    }
    repo = text_value(tool.meta, "repo_url")
    if repo:
        schema["sameAs"] = [repo]
    cover = text_value(tool.meta, "cover")
    if cover:
        schema["image"] = absolute_asset(cover)
    return schema


def build_tool_detail(tool: Document, posts: list[Document]) -> tuple[str, str]:
    name = text_value(tool.meta, "name", tool.title)
    summary = text_value(tool.meta, "summary")
    platform = text_value(tool.meta, "platform", "Windows")
    version = text_value(tool.meta, "version", "持续更新")
    category = text_value(tool.meta, "category", "效率工具")
    price_label = text_value(tool.meta, "price_label", "免费")
    license_label = text_value(tool.meta, "license_label", "查看详情")
    download_url = text_value(tool.meta, "download_url")
    download_label = text_value(tool.meta, "download_label", "立即下载")
    repo_url = text_value(tool.meta, "repo_url")
    body_html = render_markdown(tool.body)
    related_posts = [post for post in posts if text_value(post.meta, "related_tool") == tool.slug]
    related_posts_html = ""
    if related_posts:
        related_posts_html = f"""
<section class="section" aria-labelledby="related-posts-title">
  <div class="section-head"><div><span class="section-kicker">RELATED NOTES</span><h2 id="related-posts-title">与 {html.escape(name)} 相关的实战记录</h2></div></div>
  <div class="post-grid">{''.join(post_card(post) for post in related_posts)}</div>
</section>"""
    cover = text_value(tool.meta, "cover")
    cover_html = ""
    if cover:
        cover_html = f"""
<figure class="detail-cover">
  <img src="{html.escape(cover, quote=True)}" alt="{html.escape(text_value(tool.meta, "cover_alt", name), quote=True)}">
  <figcaption>{html.escape(text_value(tool.meta, "cover_caption", name + " 实际界面或效果对比"))}</figcaption>
</figure>"""
    repo_link = f'<a href="{html.escape(repo_url, quote=True)}" target="_blank" rel="noopener noreferrer">查看源码</a>' if repo_url else ""
    content = f"""
<div class="page-shell">
  <nav aria-label="面包屑">
    <ol class="breadcrumbs"><li><a href="/">首页</a></li><li><a href="/tools/">工具库</a></li><li>{html.escape(name)}</li></ol>
  </nav>
  <header class="detail-hero">
    <div class="detail-copy">
      <div class="tag-row">{tag_html(category)}{tag_html(text_value(tool.meta, "status", "已发布"), True)}</div>
      <h1>{html.escape(name)}</h1>
      <p class="summary">{html.escape(summary)}</p>
      <div class="hero-actions">
        {f'<a class="button accent" href="{html.escape(download_url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(download_label)} →</a>' if download_url else ''}
        <a class="button outline" href="#details">查看功能与说明</a>
      </div>
      {cover_html}
    </div>
    <aside class="fact-panel" aria-label="{html.escape(name)}关键信息">
      <div class="tag-row" style="margin-bottom:18px">{tag_html(price_label, True)}</div>
      <dl class="fact-list">
        <div><dt>运行平台</dt><dd>{html.escape(platform)}</dd></div>
        <div><dt>当前版本</dt><dd>{html.escape(version)}</dd></div>
        <div><dt>工具分类</dt><dd>{html.escape(category)}</dd></div>
        <div><dt>价格</dt><dd>{html.escape(price_label)}</dd></div>
        <div><dt>许可</dt><dd>{html.escape(license_label)}</dd></div>
      </dl>
      <div class="hero-actions" style="margin-top:0">
        {f'<a class="button small" href="{html.escape(download_url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(download_label)}</a>' if download_url else ''}
        {f'<a class="button outline small" href="{html.escape(repo_url, quote=True)}" target="_blank" rel="noopener noreferrer">GitHub 仓库</a>' if repo_url else ''}
      </div>
    </aside>
  </header>
  <section class="section" id="details">
    <div class="article-layout">
      <article class="tool-content">{body_html}</article>
      <aside class="article-aside">
        <strong>快速判断</strong>
        <p>{html.escape(text_value(tool.meta, "quick_take", summary))}</p>
        <strong style="margin-top:18px">{repo_link or "下载与版本"}</strong>
        <ul>
          <li>所有下载链接均指向官方发布渠道。</li>
          <li>本地运行工具不会上传你的文档内容。</li>
          <li>建议下载后先校验文件来源与版本。</li>
        </ul>
      </aside>
    </div>
  </section>
  {related_posts_html}
</div>"""
    schema = tool_schema(tool)
    title = text_value(tool.meta, "seo_title", f"{name}｜AI探索者实验室")
    description = text_value(tool.meta, "seo_description", summary)
    keywords = ",".join(text_list(tool.meta, "keywords")) or summary
    image = cover or "/favicon_io/android-chrome-512x512.png"
    return (
        page_html(
            route=f"tools/{tool.slug}.html",
            title=title,
            description=description,
            keywords=keywords,
            content=content,
            active="tools",
            schema=schema,
            image=image,
            page_type="product",
        ),
        description,
    )


def build_posts_index(posts: list[Document]) -> str:
    ordered = sorted(posts, key=post_date, reverse=True)
    cards = "".join(post_card(post) for post in ordered)
    content = f"""
<div class="page-shell">
  <header class="page-heading">
    <span class="section-kicker">FIELD NOTES</span>
    <h1>技术专栏：把踩过的坑写成下一次的捷径</h1>
    <p>记录本地 AI、跨设备工具、边缘硬件、软件打包与发布的真实工程过程。文章优先给出可复现步骤、取舍原因和失败边界。</p>
  </header>
  <section class="section" aria-label="全部技术文章">
    <div class="post-grid">{cards}</div>
  </section>
</div>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "AI探索者实验室技术专栏",
        "url": f"{SITE_URL}/posts/",
        "description": "本地AI、跨设备工具、边缘硬件与自动化发布实战文章索引。",
        "inLanguage": "zh-CN",
        "hasPart": [
            {"@type": "TechArticle", "headline": post.title, "url": f"{SITE_URL}/posts/{post.slug}.html"}
            for post in ordered
        ],
    }
    return page_html(
        route="posts/",
        title="技术专栏｜AI探索者实验室",
        description="AI探索者实验室技术专栏，记录本地离线AI、跨设备工具、Jetson与树莓派、Python打包、GitHub Release和自动化脚本实战。",
        keywords="AI技术专栏,本地AI,边缘计算,Jetson,树莓派,Python打包,PyInstaller,GitHub Release,自动化脚本,FileBeam",
        content=content,
        active="posts",
        schema=schema,
    )


def related_tool_card(tool: Document | None) -> str:
    if tool is None:
        return ""
    return f"""
<aside class="related-tool" aria-labelledby="related-tool-title">
  <div>
    <span class="section-kicker">TOOL FROM THIS NOTE</span>
    <h2 id="related-tool-title">{html.escape(text_value(tool.meta, "name", tool.title))}</h2>
    <p>{html.escape(text_value(tool.meta, "summary"))}</p>
  </div>
  <a class="button light" href="/tools/{tool.slug}.html">查看工具详情 →</a>
</aside>"""


def article_schema(post: Document) -> dict[str, Any]:
    tags = text_list(post.meta, "tags")
    schema: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": post.title,
        "description": text_value(post.meta, "summary"),
        "datePublished": post_date(post),
        "dateModified": text_value(post.meta, "updated", post_date(post)),
        "articleSection": text_value(post.meta, "category", "技术专栏"),
        "keywords": tags,
        "url": canonical_for(f"posts/{post.slug}.html"),
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical_for(f"posts/{post.slug}.html")},
        "inLanguage": "zh-CN",
        "author": {"@type": "Person", "name": SITE_AUTHOR, "url": f"{SITE_URL}/about.html"},
        "publisher": {"@type": "Person", "name": SITE_AUTHOR, "url": f"{SITE_URL}/about.html"},
    }
    image = text_value(post.meta, "cover")
    if image:
        schema["image"] = absolute_asset(image)
    return schema


def build_post_detail(post: Document, tools: list[Document]) -> str:
    category = text_value(post.meta, "category", "技术专栏")
    tags = text_list(post.meta, "tags")
    summary = text_value(post.meta, "summary")
    related_slug = text_value(post.meta, "related_tool")
    related_tool = next((tool for tool in tools if tool.slug == related_slug), None)
    body_html = render_markdown(post.body)
    read_minutes = max(4, round(len(re.sub(r"\s+", "", post.body)) / 360))
    tag_markup = "".join(tag_html(item) for item in [category, *tags])
    content = f"""
<div class="page-shell">
  <nav aria-label="面包屑">
    <ol class="breadcrumbs"><li><a href="/">首页</a></li><li><a href="/posts/">技术专栏</a></li><li>{html.escape(category)}</li></ol>
  </nav>
  <header class="article-header">
    <div class="tag-row">{tag_markup}</div>
    <h1>{html.escape(post.title)}</h1>
    <p class="dek">{html.escape(summary)}</p>
    <div class="article-meta">
      <time datetime="{html.escape(post_date(post))}">{html.escape(post_date(post))}</time>
      <span>约 {read_minutes} 分钟阅读</span>
      <span>{SITE_AUTHOR}</span>
    </div>
  </header>
  <div class="article-layout">
    <article class="content-card article-content">
      <div class="answer-box"><strong>核心结论：</strong>{html.escape(summary)}</div>
      {body_html}
    </article>
    <aside class="article-aside">
      <strong>文章信息</strong>
      <p>{html.escape(category)} · {html.escape(post_date(post))}</p>
      <strong style="margin-top:18px">适合谁读</strong>
      <p>{html.escape(text_value(post.meta, "audience", "希望把本地工具做成稳定软件产品的开发者与效率工具爱好者。"))}</p>
      <strong style="margin-top:18px">快速导航</strong>
      <ul><li><a href="#main">回到文章开头</a></li><li><a href="/posts/">更多技术文章</a></li><li><a href="/tools/">浏览工具库</a></li></ul>
    </aside>
  </div>
  {related_tool_card(related_tool)}
</div>"""
    title = text_value(post.meta, "seo_title", f"{post.title}｜AI探索者实验室")
    description = text_value(post.meta, "seo_description", summary)
    keywords = ",".join(text_list(post.meta, "keywords")) or ",".join(tags)
    return page_html(
        route=f"posts/{post.slug}.html",
        title=title,
        description=description,
        keywords=keywords,
        content=content,
        active="posts",
        schema=article_schema(post),
        image=text_value(post.meta, "cover", "/favicon_io/android-chrome-512x512.png"),
        page_type="article",
    )


def build_about() -> str:
    content = f"""
<div class="page-shell">
  <header class="page-heading">
    <span class="section-kicker">ABOUT THE EXPLORER</span>
    <h1>关于 AI 探索者：把 AI 变成手上真正能用的工具</h1>
    <p>这里不是模型资讯搬运站，而是一间持续进行本地 AI、边缘设备与效率工具实验的数字工作室。</p>
  </header>
  <section class="section">
    <div class="about-grid">
      <article class="about-panel">
        <h2>为什么做这个实验室</h2>
        <p>日常里最值得解决的问题通常并不宏大：AI 生成的 Markdown 一粘到 Word 就乱、手机和电脑之间传几张照片还要登录账号、一个脚本跑通一次却无法稳定交付给别人。</p>
        <p>AI 探索者实验室专注于把这些“小麻烦”拆开，做成可下载、可验证、可长期维护的工具。能够本地完成的事情优先留在本地；必须联网的能力会清楚说明边界。</p>
        <p>目前已归档 <a href="/tools/filebeam.html">FileBeam Lite</a> 与 <a href="/tools/wenjiang.html">文匠 Markdown_Office</a>，后续会继续覆盖本地大模型、Jetson、树莓派和自动化脚本。</p>
      </article>
      <aside class="about-panel dark">
        <span class="section-kicker">OPERATING PRINCIPLES</span>
        <h2>工作原则</h2>
        <div class="principle-list">
          <div class="principle"><strong>真实麻烦优先</strong><span>先证明问题高频，再决定是否开发。</span></div>
          <div class="principle"><strong>本地与可控</strong><span>隐私和离线能力不是附加项，而是设计约束。</span></div>
          <div class="principle"><strong>可复现交付</strong><span>能构建、能测试、能解释失败，才算完成。</span></div>
        </div>
      </aside>
    </div>
    <div class="about-grid">
      <article class="about-panel">
        <h2>关注方向</h2>
        <div class="feature-grid">
          <div class="feature-item"><strong>本地离线 AI</strong><span>本地模型、文档转换、隐私优先应用。</span></div>
          <div class="feature-item"><strong>跨设备效率</strong><span>局域网互传、桌面与手机协同。</span></div>
          <div class="feature-item"><strong>边缘硬件</strong><span>Jetson、树莓派与轻量推理服务。</span></div>
          <div class="feature-item"><strong>工程自动化</strong><span>打包、测试、发布、版本与知识归档。</span></div>
        </div>
      </article>
      <aside class="about-panel">
        <h2>联系与反馈</h2>
        <p>如果你在使用工具时遇到问题，或希望提出新的真实场景，可以通过邮箱联系。</p>
        <p><a class="button" href="mailto:{CONTACT_EMAIL}">发送邮件</a></p>
        <p>也欢迎通过每个工具页面中的 GitHub 仓库提交 Issue。</p>
      </aside>
    </div>
  </section>
</div>"""
    schema = {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "关于AI探索者",
        "url": f"{SITE_URL}/about.html",
        "description": "AI探索者实验室专注于本地离线AI、跨设备效率工具、边缘硬件与自动化脚本实战。",
        "mainEntity": {
            "@type": "Person",
            "name": SITE_AUTHOR,
            "email": CONTACT_EMAIL,
            "url": f"{SITE_URL}/about.html",
            "knowsAbout": ["本地AI", "离线应用", "FileBeam", "Markdown转Word", "Jetson", "树莓派", "自动化脚本"],
        },
    }
    return page_html(
        route="about.html",
        title="关于AI探索者｜AI探索者实验室",
        description="了解AI探索者实验室的品牌定位、工作原则与关注方向：本地离线AI、跨设备效率工具、Jetson与树莓派、自动化脚本和免费开源软件。",
        keywords="AI探索者,关于我们,AI探索者实验室,本地离线AI,跨设备工具,Jetson,树莓派,自动化脚本",
        content=content,
        active="about",
        schema=schema,
    )


def sitemap_xml(routes: list[tuple[str, str, str]]) -> str:
    rows = []
    for route, lastmod, priority in routes:
        rows.append(
            "  <url>\n"
            f"    <loc>{xml_escape(canonical_for(route))}</loc>\n"
            f"    <lastmod>{xml_escape(lastmod)}</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )


def robots_txt() -> str:
    agents = [
        "*",
        "Baiduspider",
        "Baiduspider-image",
        "Googlebot",
        "Bingbot",
        "Sogou web spider",
        "360Spider",
        "GPTBot",
        "OAI-SearchBot",
        "DeepSeekBot",
        "Bytespider",
        "ClaudeBot",
        "PerplexityBot",
        "Applebot",
    ]
    blocks = [f"User-agent: {agent}\nAllow: /" for agent in agents]
    return (
        "# AI探索者实验室 · https://wojingfang.cn\n"
        "# 允许搜索引擎与 AI 检索爬虫读取公开内容。\n\n"
        + "\n\n".join(blocks)
        + f"\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    )


def llms_txt(tools: list[Document], posts: list[Document]) -> str:
    tool_sections: list[str] = []
    for tool in tools:
        features = "；".join(text_list(tool.meta, "features"))
        tool_sections.append(
            f"### {text_value(tool.meta, 'name', tool.title)}\n\n"
            f"- 核心痛点：{text_value(tool.meta, 'pain', text_value(tool.meta, 'summary'))}\n"
            f"- 核心功能：{features or text_value(tool.meta, 'summary')}\n"
            f"- 运行平台：{text_value(tool.meta, 'platform', '未注明')}\n"
            f"- 价格：{text_value(tool.meta, 'price_label', '免费')}\n"
            f"- 官方下载：{text_value(tool.meta, 'download_url', canonical_for(f'tools/{tool.slug}.html'))}\n"
            f"- 详情页：{canonical_for(f'tools/{tool.slug}.html')}"
        )
    post_sections: list[str] = []
    for post in sorted(posts, key=post_date, reverse=True):
        post_sections.append(
            f"### {post.title}\n\n"
            f"- 发布日期：{post_date(post)}\n"
            f"- 栏目：{text_value(post.meta, 'category', '技术专栏')}\n"
            f"- 标签：{', '.join(text_list(post.meta, 'tags'))}\n"
            f"- 摘要：{text_value(post.meta, 'summary')}\n"
            f"- 直达链接：{canonical_for(f'posts/{post.slug}.html')}"
        )
    return f"""# AI探索者实验室

> 官网：{SITE_URL}/
> 定位：AI 探索者 · AI 与实用工具解决真实生活中的小麻烦

## 网站定位

AI探索者实验室专注本地离线 AI 应用、跨设备效率工具（FileBeam / 文匠）与自动化脚本实战。关注本地大模型、边缘硬件（Jetson / 树莓派）与极简桌面效率工具。所有自研免费 / 开源软件与实战踩坑记录均在此归档。

## 工具库

{chr(10).join(tool_sections)}

## 技术专栏

{chr(10).join(post_sections)}

## 重要页面

- 工具库索引：{SITE_URL}/tools/
- 技术专栏索引：{SITE_URL}/posts/
- 关于AI探索者：{SITE_URL}/about.html
- Sitemap：{SITE_URL}/sitemap.xml
- 联系方式：{CONTACT_EMAIL}
"""


def validate_outputs(
    pages: list[tuple[str, Path]],
    tools: list[Document],
    posts: list[Document],
) -> None:
    errors: list[str] = []
    canonical_values: set[str] = set()
    required_markers = [
        '<meta name="description"',
        '<meta name="keywords"',
        '<link rel="canonical"',
        "application/ld+json",
    ]
    for route, path in pages:
        if not path.is_file():
            errors.append(f"缺少输出文件: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                errors.append(f"{path}: 缺少 {marker}")
        canonical = canonical_for(route)
        if f'<link rel="canonical" href="{canonical}">' not in text:
            errors.append(f"{path}: canonical 不一致，应为 {canonical}")
        if canonical in canonical_values:
            errors.append(f"重复 canonical: {canonical}")
        canonical_values.add(canonical)
        schemas = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            text,
            flags=re.DOTALL,
        )
        for schema in schemas:
            try:
                json.loads(schema)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: JSON-LD 无效: {exc}")
        if "fonts.googleapis.com" in text or "cdn.jsdelivr.net" in text:
            errors.append(f"{path}: 生成页面包含外部字体或 CDN 依赖")

    for tool in tools:
        path = ROOT / "tools" / f"{tool.slug}.html"
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if '"@type":"SoftwareApplication"' not in text and '"@type": "SoftwareApplication"' not in text:
                errors.append(f"{path}: 缺少 SoftwareApplication JSON-LD")

    for post in posts:
        path = ROOT / "posts" / f"{post.slug}.html"
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if '"@type":"TechArticle"' not in text and '"@type": "TechArticle"' not in text:
                errors.append(f"{path}: 缺少 TechArticle JSON-LD")
            related = text_value(post.meta, "related_tool")
            if related and f'href="/tools/{related}.html"' not in text:
                errors.append(f"{path}: 缺少 related_tool 推荐卡片")

    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap_root = ET.parse(sitemap_path).getroot()
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml 无法解析: {exc}")
    else:
        namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in sitemap_root.findall("sm:url/sm:loc", namespaces)}
        for route, _path in pages:
            if canonical_for(route) not in locations:
                errors.append(f"sitemap.xml 缺少 {canonical_for(route)}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    for token in ("GPTBot", "DeepSeekBot", "Bytespider", f"{SITE_URL}/sitemap.xml"):
        if token not in robots:
            errors.append(f"robots.txt 缺少 {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for tool in tools:
        if canonical_for(f"tools/{tool.slug}.html") not in llms:
            errors.append(f"llms.txt 缺少工具 {tool.slug}")
    for post in posts:
        if canonical_for(f"posts/{post.slug}.html") not in llms:
            errors.append(f"llms.txt 缺少文章 {post.slug}")

    if errors:
        raise RuntimeError("构建验证失败:\n- " + "\n- ".join(errors))


def build() -> None:
    if not TOOLS_DIR.is_dir() or not POSTS_DIR.is_dir():
        raise RuntimeError("缺少 content/tools 或 content/posts 目录")

    tools = load_documents(TOOLS_DIR)
    posts = load_documents(POSTS_DIR)
    if not tools:
        raise RuntimeError("content/tools 下没有 Markdown 内容")
    if not posts:
        raise RuntimeError("content/posts 下没有 Markdown 内容")

    tool_slugs: set[str] = set()
    for tool in tools:
        if tool.slug in tool_slugs:
            raise RuntimeError(f"重复工具 slug: {tool.slug}")
        tool_slugs.add(tool.slug)
        if not text_value(tool.meta, "download_url"):
            raise RuntimeError(f"{tool.source}: 缺少 download_url")

    post_slugs: set[str] = set()
    for post in posts:
        if post.slug in post_slugs:
            raise RuntimeError(f"重复文章 slug: {post.slug}")
        post_slugs.add(post.slug)
        related = text_value(post.meta, "related_tool")
        if related and related not in tool_slugs:
            raise RuntimeError(f"{post.source}: related_tool={related} 不存在")
        for key in ("title", "date", "category", "tags", "summary", "related_tool"):
            if key not in post.meta:
                raise RuntimeError(f"{post.source}: Frontmatter 缺少 {key}")

    generated: list[tuple[str, Path]] = []
    outputs: list[tuple[str, str]] = []

    outputs.append(("index.html", build_home(tools, posts)))
    generated.append(("", ROOT / "index.html"))

    output_path = ROOT / "tools" / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    outputs.append(("tools/index.html", build_tools_index(tools)))
    generated.append(("tools/", output_path))

    for tool in tools:
        page, _description = build_tool_detail(tool, posts)
        path = ROOT / "tools" / f"{tool.slug}.html"
        outputs.append((f"tools/{tool.slug}.html", page))
        generated.append((f"tools/{tool.slug}.html", path))

    output_path = ROOT / "posts" / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    outputs.append(("posts/index.html", build_posts_index(posts)))
    generated.append(("posts/", output_path))

    for post in posts:
        path = ROOT / "posts" / f"{post.slug}.html"
        outputs.append((f"posts/{post.slug}.html", build_post_detail(post, tools)))
        generated.append((f"posts/{post.slug}.html", path))

    outputs.append(("about.html", build_about()))
    generated.append(("about.html", ROOT / "about.html"))

    for relative, content in outputs:
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    today = date.today().isoformat()
    sitemap_routes: list[tuple[str, str, str]] = []
    for route, _path in generated:
        sitemap_routes.append((route, today, "1.0" if route == "" else "0.8"))
    for static_route in ("activate.html", "privacy.html", "terms.html", "blog/template-test-report.html"):
        if (ROOT / static_route).is_file():
            sitemap_routes.append((static_route, today, "0.4"))

    (ROOT / "sitemap.xml").write_text(sitemap_xml(sitemap_routes), encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots_txt(), encoding="utf-8")
    (ROOT / "llms.txt").write_text(llms_txt(tools, posts), encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(
        json.dumps(
            {
                "name": SITE_NAME,
                "short_name": "AI探索者",
                "description": "AI与实用工具解决真实生活中的小麻烦",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#f2f5ef",
                "theme_color": "#0d6b55",
                "icons": [
                    {
                        "src": "/favicon_io/android-chrome-192x192.png",
                        "sizes": "192x192",
                        "type": "image/png",
                    },
                    {
                        "src": "/favicon_io/android-chrome-512x512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    validate_outputs(generated, tools, posts)
    print(f"Built {len(generated)} HTML pages from {len(tools)} tools and {len(posts)} posts.")
    for route, _path in generated:
        print(f"  - {canonical_for(route)}")
    print(f"Generated sitemap.xml ({len(sitemap_routes)} URLs), robots.txt and llms.txt.")
    print("Validation passed.")


if __name__ == "__main__":
    try:
        build()
    except Exception as error:
        print(f"Build failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
