#!/usr/bin/env python3
"""
invoice-merger: 将多个发票 PDF 两两拼合为 A4 上下结构，中间加裁剪线。

用法:
  python3 merge_invoices.py file1.pdf file2.pdf [file3.pdf ...]
  python3 merge_invoices.py /path/to/folder/   # 扫描文件夹内所有 PDF

输出:
  桌面/YYYYMMDD-发票合并/发票合并_001.pdf
"""

import sys
import os
import glob
import datetime
from pathlib import Path

# ── 依赖检查 ──────────────────────────────────────────────────────────────────
def check_deps():
    missing = []
    try:
        import pypdf
    except ImportError:
        missing.append("pypdf")
    try:
        import reportlab
    except ImportError:
        missing.append("reportlab")
    if missing:
        print(f"[错误] 缺少依赖，请先安装：pip install {' '.join(missing)}")
        sys.exit(1)

check_deps()

import pypdf
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
import io

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def get_output_dir():
    """返回桌面/YYYYMMDD-发票合并/，自动创建"""
    desktop = Path.home() / "Desktop"
    date_str = datetime.date.today().strftime("%Y%m%d")
    out_dir = desktop / f"{date_str}-发票合并"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_output_path(out_dir: Path) -> Path:
    """自动加序号，避免覆盖"""
    i = 1
    while True:
        p = out_dir / f"发票合并_{i:03d}.pdf"
        if not p.exists():
            return p
        i += 1


def collect_pdfs(args):
    """从命令行参数收集 PDF 路径列表"""
    pdfs = []
    for arg in args:
        p = Path(arg)
        if p.is_dir():
            found = sorted(p.glob("*.pdf"))
            pdfs.extend(found)
        elif p.is_file() and p.suffix.lower() == ".pdf":
            pdfs.append(p)
        else:
            print(f"[警告] 跳过无效路径: {arg}")
    return pdfs


def pdf_to_single_page_bytes(pdf_path: Path) -> bytes:
    """读取 PDF 第一页，返回该页的单页 PDF bytes"""
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def make_combined_page(top_pdf_bytes: bytes, bottom_pdf_bytes: bytes) -> bytes:
    """
    将两个 PDF 页面上下拼合为一张 A4 页面，中间加裁剪线。
    返回合并后单页 PDF 的 bytes。
    """
    A4_W, A4_H = A4  # 595.27 x 841.89 pt
    gap = 15  # 发票与裁剪线的间隙 (pt)
    half_h = A4_H / 2

    # 1. 创建底层画布（裁剪线）
    packet = io.BytesIO()
    c = rl_canvas.Canvas(packet, pagesize=A4)

    # 裁剪线：虚线（无 icon）
    c.setDash(6, 4)
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(20, half_h, A4_W - 20, half_h)
    c.setDash()  # 恢复实线

    c.save()
    packet.seek(0)
    base_pdf = PdfReader(packet)
    base_page = base_pdf.pages[0]

    # 2. 读取上下两个发票页面
    top_reader = PdfReader(io.BytesIO(top_pdf_bytes))
    bottom_reader = PdfReader(io.BytesIO(bottom_pdf_bytes))
    top_page = top_reader.pages[0]
    bottom_page = bottom_reader.pages[0]

    # 3. 将发票缩放合并到 base_page（留间隙）
    # 上半：缩放后高度为 half_h - gap，放在裁剪线上方
    top_target_h = half_h - gap
    base_page.merge_transformed_page(
        top_page,
        pypdf.Transformation().scale(
            A4_W / float(top_page.mediabox.width),
            top_target_h / float(top_page.mediabox.height)
        ).translate(0, half_h + gap/2)
    )

    # 下半：缩放后高度为 half_h - gap，放在裁剪线下方
    bottom_target_h = half_h - gap
    base_page.merge_transformed_page(
        bottom_page,
        pypdf.Transformation().scale(
            A4_W / float(bottom_page.mediabox.width),
            bottom_target_h / float(bottom_page.mediabox.height)
        ).translate(0, 0)
    )

    # 4. 输出
    writer = PdfWriter()
    writer.add_page(base_page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def open_file(path: Path):
    """跨平台预览，失败静默"""
    try:
        if sys.platform == "darwin":
            os.system(f'open "{path}"')
        elif sys.platform == "win32":
            os.startfile(str(path))
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        pass


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python3 merge_invoices.py file1.pdf [file2.pdf ...] 或 文件夹路径")
        sys.exit(1)

    pdfs = collect_pdfs(sys.argv[1:])
    if not pdfs:
        print("[错误] 未找到任何 PDF 文件")
        sys.exit(1)

    print(f"[信息] 共找到 {len(pdfs)} 个 PDF：")
    for p in pdfs:
        print(f"  - {p.name}")

    # 奇数补齐：最后一个自我复制
    if len(pdfs) % 2 != 0:
        pdfs.append(pdfs[-1])
        print(f"[信息] 奇数个文件，最后一个「{pdfs[-2].name}」将自我复制")

    # 两两配对
    pairs = [(pdfs[i], pdfs[i+1]) for i in range(0, len(pdfs), 2)]
    print(f"[信息] 共 {len(pairs)} 对，生成 {len(pairs)} 页")

    # 合并
    writer = PdfWriter()
    for i, (top_path, bottom_path) in enumerate(pairs):
        print(f"[处理] 第 {i+1} 页：{top_path.name} + {bottom_path.name}")
        top_bytes = pdf_to_single_page_bytes(top_path)
        bottom_bytes = pdf_to_single_page_bytes(bottom_path)
        combined = make_combined_page(top_bytes, bottom_bytes)
        page = PdfReader(io.BytesIO(combined)).pages[0]
        writer.add_page(page)

    # 输出
    out_dir = get_output_dir()
    out_path = get_output_path(out_dir)
    with open(out_path, "wb") as f:
        writer.write(f)

    print(f"\n✅ 完成！输出文件：{out_path}")
    print(f"   共 {len(pairs)} 页，每页含 2 张发票，打印后沿裁剪线裁开即可")

    open_file(out_path)


if __name__ == "__main__":
    main()
