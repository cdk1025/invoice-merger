# Invoice Merger - 发票合并 Skill

将一批发票文件快速整理成可打印 PDF，省纸、省时、省心。

- PDF：两两合并到同一页（上半 + 下半）
- 图片（JPG/JPEG/PNG）：四张合并到同一页（2x2）
- 每页中线自动加裁剪线，打印后更容易裁切
- 输出到输入目录下 `YYYYMMDD--已合并`

## 为什么做这个工具

常见痛点：

- 一张 A4 只打一张发票，浪费纸张
- 在线工具可能收费/有水印，还要上传隐私文件
- 手工排版耗时，重复劳动多

这个 Skill 的目标很简单：本地批量处理，零水印，低依赖，可重复使用。

## 功能说明

### 1) PDF 合并

- 两两上下排版到 A4 页面
- 每个输入 PDF 仅使用第一页
- 奇数个时，最后一个单独占上半区域（不复制）
- 输出文件名：优先 `发票合并.pdf`，重名时自动追加序号

### 2) 图片合并

- 每页按 2x2 排版：上半 1-2，下半 3-4
- 不足 4 张时按既定布局保留空位
- 自动按比例缩放并居中
- 输出文件名：优先 `账单合并.pdf`，重名时自动追加序号

### 3) 输出规则

- 输出目录：`<输入目录>/YYYYMMDD--已合并`
- 同一天重复执行会复用同名目录
- 文件名自动加序号，避免覆盖
- macOS 下会自动打开本次生成的所有输出文件预览

## 安装方式

### 方式一：ClawHub 安装（推荐）

```text
/skill install invoice-merger
```

或在 ClawHub 搜索 `invoice-merger` 一键安装。

### 方式二：本地/GitHub 安装

- 把 `invoice-merger/` 文件夹拖入 OpenClaw 对话窗口
- 或告诉 OpenClaw：`安装这个 skill：/path/to/invoice-merger`
- 或提供仓库地址让 OpenClaw 拉取安装

## 依赖

```bash
pip3 install pypdf Pillow
```

## 使用方法

### 在 OpenClaw 中对话触发

- 合并发票
- 把这个目录里的发票拼一下
- 把 PDF 和图片都整理成可打印文件

### 命令行手动运行

```bash
python3 invoice-merger/scripts/merge_invoices.py <目录路径>
```

示例：

```bash
python3 invoice-merger/scripts/merge_invoices.py ~/Desktop/invoices
```

## 输出示例

```text
invoices/
└── 20260324--已合并/
    ├── 发票合并.pdf
    └── 账单合并.pdf
```

## 项目结构

```text
invoice-merger-github/
├── README.md
├── CLAWHUB.md
└── invoice-merger/
    ├── SKILL.md
    └── scripts/
        └── merge_invoices.py
```

## FAQ

**Q: 支持哪些输入格式？**  
A: `.pdf`、`.jpg`、`.jpeg`、`.png`（不区分大小写）。

**Q: PDF 会处理多页吗？**  
A: 当前每个输入 PDF 只取第一页。

**Q: 会上传文件到云端吗？**  
A: 不会，默认本地处理。

## License

MIT
