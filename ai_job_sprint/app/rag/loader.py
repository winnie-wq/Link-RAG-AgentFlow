from pathlib import Path

from pypdf import PdfReader


def load_txt_or_markdown(
    file_path: str,
):

    path = Path(file_path)

    return path.read_text(encoding="utf-8")


def load_pdf(
    file_path: str,
):

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        # 提取pdf内容
        text = page.extract_text() or ""

        pages.append(
            {
                "page": page_number,
                "text": text,
            }
        )

    return pages


def load_document(
    file_path: str,
):

    path = Path(file_path)

    # 提取文件后缀
    suffix = path.suffix.lower()

    if suffix in {
        ".txt",
        ".md",
    }:

        return {
            "type": "text",
            "source": path.name,
            "text": load_txt_or_markdown(file_path),
        }

    if suffix == ".pdf":

        return {
            "type": "pdf",
            "source": path.name,
            "pages": load_pdf(file_path),
        }

    raise ValueError(f"暂不支持的文件类型: {suffix}")
