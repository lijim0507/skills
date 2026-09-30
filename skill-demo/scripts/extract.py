"""从 PDF 文件中提取文本内容。"""

import argparse
import os
import sys

MAX_SIZE_MB = 100


def validate_pdf_input(file_path):
    """校验 PDF 文件输入是否有效，返回 (是否有效, 错误信息)。"""
    if not file_path:
        return False, "错误：未提供文件路径"
    if not os.path.exists(file_path):
        return False, f"错误：文件不存在 → {file_path}"
    if not file_path.lower().endswith(".pdf"):
        actual = os.path.splitext(file_path)[1] or "（无扩展名）"
        return False, f"错误：文件类型不支持，期望 .pdf，实际 → {actual}"
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        print(f"警告：文件较大（{size_mb:.1f} MB），处理可能较慢")
    return True, ""


def extract_text(file_path, start_page=1, max_pages=None):
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    total = len(reader.pages)
    end = total if max_pages is None else min(total, start_page - 1 + max_pages)
    parts = []
    for index in range(start_page - 1, end):
        parts.append(reader.pages[index].extract_text() or "")
    return total, "\n".join(parts)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="PDF 文本提取脚本")
    parser.add_argument("file", help="必填：PDF 文件路径")
    parser.add_argument("--start-page", type=int, default=1, help="可选：起始页码，默认 1")
    parser.add_argument("--max-pages", type=int, default=None, help="可选：最多提取的页数，默认全部")
    args = parser.parse_args()

    ok, message = validate_pdf_input(args.file)
    if not ok:
        print(message)
        sys.exit(1)

    try:
        total, text = extract_text(args.file, args.start_page, args.max_pages)
    except ImportError:
        print("错误：缺少依赖 pypdf，请先执行 pip install pypdf")
        sys.exit(1)

    print(f"文件：{os.path.basename(args.file)}")
    print(f"总页数：{total}")
    if args.max_pages is not None:
        print(f"本次提取：第 {args.start_page} 页起的最多 {args.max_pages} 页")
    print()
    print(text)


if __name__ == "__main__":
    main()