---
name: invoice-merger
description: 发票 PDF 合并工具。将多个发票 PDF 两两拼合为 A4 上下结构，中间加裁剪线，方便打印后裁开。触发场景：(1) 用户说"合并发票"、"把发票拼一起"、"两张发票打一张纸"；(2) 用户提到 PDF 合并用于打印；(3) 用户需要将多个 PDF 缩放拼到一页。支持文件夹路径或多个文件路径，奇数个文件自动将最后一个复制补齐。
---

# Invoice Merger - 发票合并工具

将多个发票 PDF 两两拼合为 A4 上下结构，中间加裁剪线，打印后沿裁剪线裁开即可。

## 功能说明

- **上下结构**：两个发票上下拼在一页 A4 纸上
- **自动裁剪线**：中间虚线 + ✂ 符号
- **奇数补齐**：奇数个文件时，最后一个自动复制补齐
- **自动命名**：输出到桌面 `YYYYMMDD-发票合并/` 目录，文件名自动加序号

## 处理逻辑

| 输入文件数 | 处理方式 | 输出页数 |
|-----------|---------|---------|
| 1 个 | 自我复制，上下拼 1 页 | 1 页 |
| 2 个 | A+B 上下拼 1 页 | 1 页 |
| 3 个 | A+B 拼 1 页，C+C 拼 1 页 | 2 页 |
| 4 个 | A+B 拼 1 页，C+D 拼 1 页 | 2 页 |
| 5 个 | A+B、C+D 各拼 1 页，E+E 拼 1 页 | 3 页 |

## 使用方法

调用脚本：

```bash
python3 ~/.qclaw/skills/invoice-merger/scripts/merge_invoices.py <文件或文件夹路径...>
```

**示例：**

```bash
# 指定多个文件
python3 ~/.qclaw/skills/invoice-merger/scripts/merge_invoices.py 发票1.pdf 发票2.pdf 发票3.pdf

# 指定文件夹（自动扫描所有 PDF）
python3 ~/.qclaw/skills/invoice-merger/scripts/merge_invoices.py /path/to/发票目录/
```

## 依赖

- Python 3
- pypdf
- reportlab

安装依赖：

```bash
pip3 install pypdf reportlab
```

## 输出

- 路径：桌面 `YYYYMMDD-发票合并/发票合并_XXX.pdf`
- 自动打开预览（支持 macOS / Windows）

## 注意事项

- 所有输入 PDF 只取第一页
- 输出文件自动加序号避免覆盖
- 裁剪线为虚线样式，打印后沿虚线裁开即可