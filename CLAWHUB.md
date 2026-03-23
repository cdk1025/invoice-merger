# Invoice Merger - OpenClaw Skill

发票合并工具，将多个发票 PDF 两两拼合为 A4 上下结构，省纸、省钱、省心。

---

## 为什么做这个工具

打印发票时，一张 A4 纸打一张发票太浪费，也不符合财务归档要求（发票大小约 A4 一半）。市面上的解决方案：

- **WPS**：会员功能，要收费
- **在线工具**：要么收费，要么有水印，还要上传文件到第三方服务器

于是用 OpenClaw 自己做了一个，打印效果不错，又参考付费软件加上了裁剪线。既然好用，不如分享出来让更多人免费用。

---

## 安装

### OpenClaw 产品（推荐）

支持 QClaw、WorkBuddy 等 OpenClaw 系列产品。

将 `invoice-merger` 文件夹拖拽到 OpenClaw 对话窗口，或告诉 OpenClaw：
```
安装这个 skill：/path/to/invoice-merger
```

### 命令行使用

```bash
pip install pypdf reportlab
python scripts/merge_invoices.py /path/to/invoices/
```

---

## 使用示例

```
用户：合并下发票文件夹里的 PDF
用户：把这三个发票合并一下
用户：帮我合并桌面上 /发票 目录下的所有 PDF
```

---

## 发布

- **GitHub**: https://github.com/cdk1025/invoice-merger
- **ClawHub**: https://clawhub.com（搜索 invoice-merger）

---

## 效果预览

> 截图放在 `screenshots/` 目录

| 合并前 | 合并后 |
|-------|-------|
| 两张独立 PDF，各占一张 A4 | 一张 A4 上下拼合，中间裁剪线 |

---

## License

MIT