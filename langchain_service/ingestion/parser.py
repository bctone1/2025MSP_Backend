from __future__ import annotations
from pathlib import Path
from typing import TypedDict, List
from .preprocess.split_pdf import split_pdf
from .preprocess.analyzer_upstage import LayoutAnalyzer
from .preprocess.extract_assets import extract_blocks_and_images, Block
from .preprocess.render_html_md import render_all

class ParseOutput(TypedDict):
    html_path: str
    md_path: str
    blocks: List[Block]
    images: List[str]

def parse_to_md_html(
    input_pdf: str | Path,
    work_dir: str | Path | None = None,
    upstage_key: str | None = None,
    batch_size: int = 10,
) -> ParseOutput:
    input_pdf = Path(input_pdf)
    work_dir = Path(work_dir or input_pdf.with_suffix(""))  # 같은 prefix 폴더
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1) 분할
    parts = split_pdf(input_pdf, out_dir=work_dir, batch_size=batch_size)

    # 2) 레이아웃 분석
    analyzer = LayoutAnalyzer(api_key=upstage_key)
    json_paths = [analyzer.analyze(p) for p in parts]

    # 3) 블록+이미지 추출
    blocks, images = extract_blocks_and_images(pdf_path=input_pdf, json_paths=json_paths, out_dir=work_dir)

    # 4) HTML/MD 렌더
    result = render_all(blocks, out_dir=work_dir, base_name=input_pdf.stem)

    return {
        "html_path": result["html_path"],
        "md_path": result["md_path"],
        "blocks": blocks,
        "images": images,
    }
