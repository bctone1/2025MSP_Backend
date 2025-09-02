import shutil
from pathlib import Path

# def split_pdf(filepath, batch_size=10):

try:  # pragma: no cover - fall back when optional dependency missing
    from pypdf import PdfReader, PdfWriter  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = PdfWriter = None

def split_pdf(filepath, out_dir: Path | str | None = None, batch_size: int = 10):
    """
    입력 PDF를 여러 개의 작은 PDF 파일로 분할
    Parameters
    ----------
    filepath : str | Path
        분할할 원본 PDF 경로.
    out_dir : str | Path | None, optional
        출력 PDF 파일이 저장될 디렉터리. 지정하지 않으면
        `filepath`와 같은 디렉터리가 사용됩니다.
    batch_size : int, optional
        분할할 페이지 묶음 크기.
    """
    filepath = Path(filepath)
    out_dir = Path(out_dir) if out_dir else filepath.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = filepath.stem

    if PdfReader is None or PdfWriter is None:
        # pypdf not available; create a single copy
        output_file = out_dir / f"{base_name}_0000_0000.pdf"
        shutil.copyfile(filepath, output_file)
        return [str(output_file)]

    reader = PdfReader(str(filepath))
    num_pages = len(reader.pages)
    print(f"총 페이지 수: {num_pages}")

    ret: list[str] = []

    for start_page in range(0, num_pages, batch_size):
        end_page = min(start_page + batch_size, num_pages) - 1

        output_file = out_dir / f"{base_name}_{start_page:04d}_{end_page:04d}.pdf"
        print(f"분할 PDF 생성: {output_file}")

        writer = PdfWriter()
        for i in range(start_page, end_page + 1):
            writer.add_page(reader.pages[i])

        with output_file.open("wb") as f:
            writer.write(f)

        ret.append(str(output_file))

    return ret

# 예시
# sample_data = "test.pdf"
# split_files = split_pdf(sample_data, batch_size=10)
