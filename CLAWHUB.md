# Invoice Merger - OpenClaw Skill

发票合并工具：将 PDF 和图片发票批量整理为可打印 PDF。

## 核心能力

- PDF：两两上下合并到 A4 页面
- 图片（JPG/JPEG/PNG）：四张按 2x2 合并到 A4 页面
- 上下半页中线自动加入裁剪线
- 输出目录：`<输入目录>/YYYYMMDD--已合并`
- 输出文件命名：优先基础名，重名时自动加序号
  - `发票合并.pdf` -> `发票合并_001.pdf`
  - `账单合并.pdf` -> `账单合并_001.pdf`

## 安装

### OpenClaw 产品

将 `invoice-merger` 文件夹拖拽到 OpenClaw 对话窗口，或告诉 OpenClaw：

```text
安装这个 skill：/path/to/invoice-merger
```

### ClawHub

```text
npx clawhub@latest install cdk1025/invoice-merger
```

## 依赖

```bash
pip3 install pypdf Pillow
```

## 运行方式

```bash
python3 invoice-merger/scripts/merge_invoices.py <目录路径>
```

## 触发示例

- 合并发票
- 把这个目录里的发票拼一下
- 把 PDF 和图片发票整理成可打印文件

## 说明

- PDF 仅处理每个输入文件的第一页
- macOS 下自动打开本次生成的所有输出文件

## License

MIT
