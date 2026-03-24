#!/usr/bin/env python3
"""
发票合并工具
1. PDF 文件：两两合并一页（上下结构），输出 1 个 PDF
2. 图片文件：四个合并一页（上半 1-2，下半 3-4），输出 1 个 PDF
3. 输出目录：输入目录下 YYYYMMDD--已合并
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageOps
    from pypdf import PageObject, PdfReader, PdfWriter, Transformation
    from pypdf.generic import DecodedStreamObject, NameObject
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip3 install pypdf Pillow")
    sys.exit(1)

A4_WIDTH_PT = 595.2756
A4_HEIGHT_PT = 841.8898
MARGIN_PT = 15.0

IMAGE_DPI = 150
A4_WIDTH_PX = int(round(A4_WIDTH_PT / 72 * IMAGE_DPI))
A4_HEIGHT_PX = int(round(A4_HEIGHT_PT / 72 * IMAGE_DPI))
IMAGE_OUTER_MARGIN_PX = 12
IMAGE_CELL_PADDING_PX = 8
IMAGE_COL_GAP_PX = 12
IMAGE_ROW_GAP_PX = 18


def get_files(directory, extensions):
    """获取目录下指定扩展名的文件（不区分大小写）"""
    ext_set = {ext.lower() for ext in extensions}
    return sorted(
        p for p in Path(directory).iterdir() if p.is_file() and p.suffix.lower() in ext_set
    )


def create_output_dir(input_dir):
    """在输入目录下创建：YYYYMMDD--已合并"""
    ts = datetime.now().strftime("%Y%m%d")
    output_dir = input_dir / f"{ts}--已合并"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def indexed_output_path(output_dir, base_name):
    """优先使用 base_name.pdf，重名时追加序号"""
    first = output_dir / f"{base_name}.pdf"
    if not first.exists():
        return first

    idx = 1
    while True:
        output = output_dir / f"{base_name}_{idx:03d}.pdf"
        if not output.exists():
            return output
        idx += 1


def merge_page_into_box(target_page, src_page, x1, y1, x2, y2):
    """将 src_page 按比例缩放并居中放入目标区域"""
    src_w = float(src_page.mediabox.width)
    src_h = float(src_page.mediabox.height)
    src_x = float(src_page.mediabox.left)
    src_y = float(src_page.mediabox.bottom)

    box_w = x2 - x1
    box_h = y2 - y1
    if src_w <= 0 or src_h <= 0 or box_w <= 0 or box_h <= 0:
        return

    scale = min(box_w / src_w, box_h / src_h)
    draw_w = src_w * scale
    draw_h = src_h * scale

    tx = x1 + (box_w - draw_w) / 2 - src_x * scale
    ty = y1 + (box_h - draw_h) / 2 - src_y * scale

    transform = Transformation().scale(scale, scale).translate(tx, ty)
    target_page.merge_transformed_page(src_page, transform)


def create_pdf_cut_line_overlay():
    """创建仅包含中间裁剪虚线的覆盖页"""
    y = A4_HEIGHT_PT / 2
    x1 = MARGIN_PT
    x2 = A4_WIDTH_PT - MARGIN_PT

    content = (
        "q\n"
        "0.6 w\n"
        "[6 3] 0 d\n"
        "0.55 0.55 0.55 RG\n"
        f"{x1:.2f} {y:.2f} m\n"
        f"{x2:.2f} {y:.2f} l\n"
        "S\n"
        "Q\n"
    )

    overlay = PageObject.create_blank_page(width=A4_WIDTH_PT, height=A4_HEIGHT_PT)
    stream = DecodedStreamObject()
    stream.set_data(content.encode("ascii"))
    overlay[NameObject("/Contents")] = stream
    return overlay


def add_pdf_cut_line(page):
    """将裁剪线覆盖页叠加到目标页"""
    page.merge_page(create_pdf_cut_line_overlay())


def merge_pdfs_two(pdf_files, output_dir):
    """PDF 两两合并（上下结构），输出 1 个 PDF（多页）"""
    if not pdf_files:
        return None

    output_file = indexed_output_path(output_dir, "发票合并")
    writer = PdfWriter()

    for i in range(0, len(pdf_files), 2):
        pair = pdf_files[i : i + 2]
        page = writer.add_blank_page(width=A4_WIDTH_PT, height=A4_HEIGHT_PT)

        try:
            top_reader = PdfReader(str(pair[0]))
            if top_reader.pages:
                merge_page_into_box(
                    page,
                    top_reader.pages[0],
                    MARGIN_PT,
                    A4_HEIGHT_PT / 2 + MARGIN_PT,
                    A4_WIDTH_PT - MARGIN_PT,
                    A4_HEIGHT_PT - MARGIN_PT,
                )
        except Exception as e:
            print(f"  ⚠ PDF 读取失败: {pair[0].name}, {e}")

        if len(pair) > 1:
            try:
                bottom_reader = PdfReader(str(pair[1]))
                if bottom_reader.pages:
                    merge_page_into_box(
                        page,
                        bottom_reader.pages[0],
                        MARGIN_PT,
                        MARGIN_PT,
                        A4_WIDTH_PT - MARGIN_PT,
                        A4_HEIGHT_PT / 2 - MARGIN_PT,
                    )
            except Exception as e:
                print(f"  ⚠ PDF 读取失败: {pair[1].name}, {e}")

        add_pdf_cut_line(page)
        print(
            f"✅ PDF 合并: {pair[0].name}"
            f" + {pair[1].name if len(pair) > 1 else ''}"
        )

    with output_file.open("wb") as f:
        writer.write(f)

    print(f"📄 PDF 输出: {output_file.name}")
    return output_file


def paste_image_to_box(page_img, img_path, box):
    """将图片按比例缩放并居中粘贴到 box 区域"""
    x1, y1, x2, y2 = box
    target_w = x2 - x1 - IMAGE_CELL_PADDING_PX * 2
    target_h = y2 - y1 - IMAGE_CELL_PADDING_PX * 2
    if target_w <= 0 or target_h <= 0:
        return

    with Image.open(img_path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        ratio = min(target_w / img.width, target_h / img.height)
        new_w = max(1, int(round(img.width * ratio)))
        new_h = max(1, int(round(img.height * ratio)))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        px = x1 + (x2 - x1 - new_w) // 2
        py = y1 + (y2 - y1 - new_h) // 2
        page_img.paste(resized, (px, py))


def draw_image_cut_line(page_img, y):
    """在图片页面中间绘制虚线裁剪线"""
    draw = ImageDraw.Draw(page_img)
    x_start = IMAGE_OUTER_MARGIN_PX
    x_end = A4_WIDTH_PX - IMAGE_OUTER_MARGIN_PX
    dash = 18
    gap = 10
    x = x_start
    while x < x_end:
        x2 = min(x + dash, x_end)
        draw.line([(x, y), (x2, y)], fill=(120, 120, 120), width=2)
        x += dash + gap


def merge_images_four(image_files, output_dir):
    """图片四个合并一页（上半 1-2，下半 3-4），输出 1 个 PDF（多页）"""
    if not image_files:
        return None

    output_file = indexed_output_path(output_dir, "账单合并")
    pages = []

    usable_w = A4_WIDTH_PX - 2 * IMAGE_OUTER_MARGIN_PX - IMAGE_COL_GAP_PX
    usable_h = A4_HEIGHT_PX - 2 * IMAGE_OUTER_MARGIN_PX - IMAGE_ROW_GAP_PX
    cell_w = usable_w // 2
    cell_h = usable_h // 2

    left_x1 = IMAGE_OUTER_MARGIN_PX
    left_x2 = left_x1 + cell_w
    right_x1 = left_x2 + IMAGE_COL_GAP_PX
    right_x2 = right_x1 + cell_w

    top_y1 = IMAGE_OUTER_MARGIN_PX
    top_y2 = top_y1 + cell_h
    bottom_y1 = top_y2 + IMAGE_ROW_GAP_PX
    bottom_y2 = bottom_y1 + cell_h

    cut_line_y = (top_y2 + bottom_y1) // 2

    boxes = [
        (left_x1, top_y1, left_x2, top_y2),
        (right_x1, top_y1, right_x2, top_y2),
        (left_x1, bottom_y1, left_x2, bottom_y2),
        (right_x1, bottom_y1, right_x2, bottom_y2),
    ]

    for i in range(0, len(image_files), 4):
        group = image_files[i : i + 4]
        page = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")

        for idx, img_path in enumerate(group):
            try:
                paste_image_to_box(page, img_path, boxes[idx])
            except Exception as e:
                print(f"  ⚠ 图片加载失败: {img_path.name}, {e}")

        draw_image_cut_line(page, cut_line_y)
        pages.append(page)
        print(f"✅ 图片合并: {len(group)} 张")

    first, *rest = pages
    first.save(
        output_file,
        "PDF",
        resolution=IMAGE_DPI,
        save_all=True,
        append_images=rest,
    )

    for page in pages:
        page.close()

    print(f"🖼️ 图片 PDF 输出: {output_file.name}")
    return output_file


def process_directory(input_path):
    """处理目录"""
    input_path = Path(input_path).resolve()

    if not input_path.exists() or not input_path.is_dir():
        print(f"❌ 目录不存在: {input_path}")
        return []

    pdf_files = get_files(input_path, [".pdf"])
    image_files = get_files(input_path, [".jpg", ".jpeg", ".png"])

    print(f"📄 找到 {len(pdf_files)} 个 PDF")
    print(f"🖼️ 找到 {len(image_files)} 个图片")

    if not pdf_files and not image_files:
        print("❌ 未找到可处理文件")
        return []

    output_dir = create_output_dir(input_path)
    print(f"📁 输出目录: {output_dir.name}")

    outputs = []

    pdf_output = merge_pdfs_two(pdf_files, output_dir)
    if pdf_output:
        outputs.append(pdf_output)

    image_output = merge_images_four(image_files, output_dir)
    if image_output:
        outputs.append(image_output)

    print(f"\n🎉 完成！共生成 {len(outputs)} 个文件")
    for out in outputs:
        print(f"   - {out.name}")

    return outputs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 merge_invoices.py <目录路径>")
        sys.exit(1)

    output_files = process_directory(sys.argv[1])

    if output_files and sys.platform == "darwin":
        for output_file in output_files:
            subprocess.run(["open", str(output_file)], check=False)
