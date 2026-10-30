# pdf_utils.py —— 把简历文件（PDF / TXT）读成纯文本
#
# 真实场景里简历几乎都是 PDF，这份文件负责把 PDF 里的文字抽出来，
# 这样后面的解析 / 匹配 / 初筛才能处理。TXT 直接读，PDF 用 PyMuPDF 抽文字。


def extract_text(filename: str, data: bytes) -> str:
    """根据文件名后缀，把上传的字节内容转成纯文本。

    filename: 文件名（用来判断是 .pdf 还是 .txt）
    data:     文件的二进制内容（Streamlit 上传拿到的就是 bytes）
    """
    if filename.lower().endswith(".pdf"):
        return _extract_pdf(data)
    # TXT / 其他文本：尝试几种常见中文编码，依次兜底
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="ignore")


def _extract_pdf(data: bytes) -> str:
    """用 PyMuPDF 把 PDF 每页文字拼起来。"""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # 老版本兼容
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip() or "[PDF 未提取到文字，可能是图片型简历]"
    except Exception as e:
        return f"[PDF 解析失败：{e}]"
