from __future__ import annotations
from typing import TypedDict, List
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from .extract_assets import Block

class RenderResult(TypedDict):
    html_path: str
    md_path: str

def render_html(blocks: List[Block], out_html: str | Path) -> str:
    html_parts = []
    for b in blocks:
        if b.get("html"):
            # figure src는 extract 단계에서 상대경로로 치환 가능. 여기서는 그대로 사용.
            html_parts.append(b["html"])
        elif b.get("text"):
            html_parts.append(f"<p>{b['text']}</p>")
    html = "\n".join(html_parts)
    out_html = Path(out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf-8")
    return str(out_html)

def render_markdown_from_html(in_html: str | Path, out_md: str | Path) -> str:
    html = Path(in_html).read_text(encoding="utf-8")
    md_txt = md(html)
    out_md = Path(out_md)
    out_md.write_text(md_txt, encoding="utf-8")
    return str(out_md)

def render_all(blocks: List[Block], out_dir: str | Path, base_name: str) -> RenderResult:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"{base_name}.html"
    md_path   = out_dir / f"{base_name}.md"
    render_html(blocks, html_path)
    render_markdown_from_html(html_path, md_path)
    return {"html_path": str(html_path), "md_path": str(md_path)}
