from __future__ import annotations
from typing import TypedDict, Literal, Optional, List, Dict, Any
from pathlib import Path
import json, os

# 충돌  문제 해결하기 위해서 fitz 강제
import pymupdf as fitz
from glob import glob
from PIL import Image
# from pdf2image import convert_from_path
from bs4 import BeautifulSoup
from markdownify import markdownify as markdown

BlockType = Literal["text","table","figure"]

class Block(TypedDict, total=False):
    text: str
    block_type: BlockType
    page_num: int
    coords: Dict[str, float]
    caption: Optional[str]
    html: Optional[str]

def _load_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _page_sizes(j: Dict[str, Any]) -> Dict[int, list[float]]:
    sizes: Dict[int, list[float]] = {}
    for p in j.get("metadata", {}).get("pages", []):
        sizes[p["page"]] = [p["width"], p["height"]]
    return sizes

def _norm_bbox(coords: list[Dict[str, float]], wh: list[float]) -> tuple[float,float,float,float]:
    xs = [c["x"] for c in coords]; ys = [c["y"] for c in coords]
    x1,y1,x2,y2 = min(xs), min(ys), max(xs), max(ys)
    w,h = wh
    return (x1/w, y1/h, x2/w, y2/h)

def _crop(img: Image.Image, nb: tuple[float,float,float,float], out_path: str | Path) -> None:
    x1,y1,x2,y2 = nb
    W,H = img.size
    box = (int(x1*W), int(y1*H), int(x2*W), int(y2*H))
    img.crop(box).convert("RGB").save(out_path)

# def pdf_page_to_image(pdf_path: str | Path, page_num_1based: int, dpi: int = 300) -> Image.Image:
#     images = convert_from_path(str(pdf_path), dpi=dpi,
#                                first_page=page_num_1based, last_page=page_num_1based)
#     if not images:
#         raise ValueError(f"페이지 {page_num_1based} 렌더 실패")
#     return images[0]

def pdf_page_to_image(pdf_path: str | Path, page_num_1based: int, dpi: int = 300) -> Image.Image:
    with fitz.open(pdf_path) as doc:
        page = doc[page_num_1based - 1]
        zoom = dpi / 72.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        return img.convert("RGB")




def extract_blocks_and_images(
    pdf_path: str | Path,
    json_paths: list[str | Path],
    out_dir: str | Path,
) -> tuple[list[Block], list[str]]:
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_images: list[str] = []
    blocks: list[Block] = []

    for jp in sorted(json_paths):
        j = _load_json(jp)
        sizes = _page_sizes(j)

        name_parts = Path(jp).stem.split("_")
        try:
            start_page = int(name_parts[-2])
        except Exception:
            start_page = 0

        for el in j.get("elements", []):
            cat = el.get("category")
            rel_page = int(el.get("page", 1))
            abs_page = start_page + rel_page
            b: Block = {
                "block_type": "text" if cat not in ("figure", "table") else cat,
                "page_num": abs_page,
                "html": el.get("html"),
            }
            text = el.get("text")
            if text:
                b["text"] = text

            if cat == "figure":
                coords = el.get("bounding_box", [])
                nb = _norm_bbox(coords, sizes.get(rel_page, [612, 792]))
                img = pdf_page_to_image(pdf_path, abs_page)
                out_img = out_dir / f"page_{abs_page}_figure_{len([p for p in saved_images if f'page_{abs_page}_' in p])+1}.png"
                _crop(img, nb, out_img)
                saved_images.append(str(out_img))
            blocks.append(b)
    return blocks, saved_images


class PDFImageProcessor:
    """
    PDF 이미지 추출 및 HTML/Markdown 변환기 (pdf2image 사용)
    """

    def __init__(self, pdf_file: str, json_files: Optional[List[str]] = None,
                 output_folder: Optional[str] = None, dpi: int = 300):
        """
        :param pdf_file: PDF 파일 경로
        :param json_files: 사용할 JSON 목록(없으면 prefix 자동 탐색)
        :param output_folder: 산출물 폴더(없으면 <pdf_stem>/)
        :param dpi: 페이지 렌더링 DPI
        """
        self.pdf_file = pdf_file
        base = os.path.splitext(pdf_file)[0]
        self.json_files = sorted(json_files or glob(base + "*.json"))
        self.output_folder = output_folder or base
        self.filename = os.path.basename(base)
        self.dpi = dpi    # Dots Per Inch  1인치 안에 몇개 찍는지 해상도 높이면 선명

    def extract_images(self) -> None:
        """JSON을 읽어 figure 크롭, HTML/MD 생성."""
        os.makedirs(self.output_folder, exist_ok=True)

        figure_count: Dict[int, int] = {}
        html_content: List[str] = []

        for json_file in self.json_files:
            json_data = _load_json(json_file)
            page_sizes = _page_sizes(json_data)

            parts = os.path.basename(json_file).split("_")
            try:
                start_page = int(parts[1])
            except (IndexError, ValueError):
                start_page = 0

            for element in json_data.get("elements", []):
                if element.get("category") == "figure":
                    rel_page = element["page"]
                    page_num = start_page + rel_page

                    coords = element["bounding_box"]
                    output_size = page_sizes.get(rel_page, [612, 792])
                    pdf_img = pdf_page_to_image(self.pdf_file, page_num, dpi=self.dpi)
                    norm_coords = _norm_bbox(coords, output_size)

                    figure_count[page_num] = figure_count.get(page_num, 0) + 1
                    output_file = os.path.join(
                        self.output_folder,
                        f"page_{page_num}_figure_{figure_count[page_num]}.png",
                    )
                    _crop(pdf_img, norm_coords, output_file)

                    soup = BeautifulSoup(element.get("html", ""), "html.parser")
                    img_tag = soup.find("img")
                    if img_tag:
                        rel_path = os.path.relpath(output_file, self.output_folder)
                        img_tag["src"] = rel_path.replace("\\", "/")
                    element["html"] = str(soup)

                html_content.append(element.get("html", ""))

        html_path = os.path.join(self.output_folder, f"{self.filename}.html")
        combined_html = "\n".join(html_content)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(combined_html)

        md_path = os.path.join(self.output_folder, f"{self.filename}.md")
        md_out = markdown(combined_html)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_out)
