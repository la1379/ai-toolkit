---
name: ocr-vision
description: >
  从图片/截图/PDF 页面提取文字（含表格、数字、代码）。三级降级：MiMo V2.5 →
  DeepSeek 视觉 → 本地 Tesseract。包含实测的开关参数与成本数据。
  触发词：识图、OCR、截图转文字、提取图片文字、PDF 页面识别、表格识别。
license: CC-BY-4.0
version: 1.0.0
---

# 识图/OCR Skill

## 调用方式

当需要从图片、PDF截图、手机截屏中提取文字时，按优先级选择方案。

---

## 输入契约

- 输入：一张或多张图片/截图，或 PDF 页面。
- 需要知道的：是否要保留表格结构、是否只要某一块区域、输出到文件还是直接返回。
- 图片 >10MB 先压缩/裁剪；扫描件优先渲染成 200dpi 再识别。

## 输出契约

- 默认输出纯文本；表格尽量转 Markdown；多张图逐张分隔。
- 每张失败要留 `!! 识别失败：<原因>`，不能让整批静默中断。
- 结果必须能落盘（Windows 终端直接 print 中文会 GBK 报错）。

## 验收清单

- [ ] 数字、金额、单位逐字核对过
- [ ] 表格行列没有错位
- [ ] 失败项有显式标记，没有假装成功
- [ ] 临时图片已清理，原始文件没动

---

## 适用场景

- 页面/App 截图、对话框截图的文字提取（含表格、数字、代码）
- PPT 幻灯片截图的文字提取
- PDF 页面渲染+文字提取
- 手机拍摄的幻灯片/文档照片 OCR
- 图片中的思维导图、表格、分类图提取

---

## 方案 A（首选）：小米 MiMo V2.5 读图

零依赖、免费余额、中文友好。**配套脚本：本 skill 目录下的 `ocr_mimo.py`**

```bash
python skills/ocr-vision/ocr_mimo.py 图片路径
python skills/ocr-vision/ocr_mimo.py 图1.jpg 图2.png          # 多张，逐张识别
python skills/ocr-vision/ocr_mimo.py --out result.txt 图.jpg   # 写入文件
python skills/ocr-vision/ocr_mimo.py --prompt "只提取表格" 图.jpg
```

凭证优先读环境变量 `MIMO_API_KEY`（可选 `MIMO_BASE_URL`）；没设时回退到 cc-switch 的本地库。

要点（都是实测踩出来的，别改）：

- **模型必须是 `mimo-v2.5`。** `mimo-v2.5-pro` 是**纯文本**模型，发图会返回
  `404 No endpoints found that support image input`。名字像升级版，其实不能读图。
- **key 从环境变量 `MIMO_API_KEY` 取**。不要用当前激活供应商的通用 token
  （例如 Claude Code 的 `ANTHROPIC_AUTH_TOKEN`）—— 那多半是别家的 key，打小米端点必 401。
  如果你用 cc-switch，也可以从它的 `providers` 表里按名字取，但这属于可选的本机做法。
- **端点**：`https://api.xiaomimimo.com/anthropic/v1/messages`（Anthropic 格式，
  不是 OpenAI 的 `/chat/completions`）。不带 `/anthropic` 前缀的那条路 404。
- **关思维链**：请求体里带 `"thinking": {"type": "disabled"}`。这是「看一眼抄下来」的活，
  不需要推理；开着会白白多烧一倍输出 token，抄写准确率没有区别。
- **成本**：一帧约 ¥0.0009（960×540 图 ≈ 790 输入 + 50 输出 token）。
- 多张图：脚本已支持，单张失败不拖垮整批，失败的那张会在结果里留 `!! 识别失败：` 标记。
- 图片过大（>10MB）：先压缩/裁剪再识别。

### 准确率实测（2026-09-19）

| 素材 | 结果 |
|---|---|
| 合成 PPT 幻灯片（6 项可验证真值：百分比/数量/表格） | **6/6 逐字吻合**，且自动把表格渲染成 markdown |
| 真实屏幕帧（终端窗口 + 浏览器 + 侧栏） | 6/6 吻合，含 `auto mode on · 2 shells`、`¥5.28` 这类细节，零幻觉 |

弱项：**极细小的文字**（完整文件路径、代码里的文件名）偶尔会漏，只说个大概。
这种场景优先试方案 B。

---

## 方案 B（次选）：DeepSeek 视觉模型

小米不可用（限流/网络/余额）时用。识别准确，**细粒度 OCR 比方案 A 更稳**，但走你自己的付费余额。

```bash
node -e "
const fs = require('fs');
const key = process.env.DEEPSEEK_API_KEY;
if (!key) { console.error('缺少 DEEPSEEK_API_KEY'); process.exit(1); }
const file = process.argv[1];   // 图片路径作为参数
const b64 = fs.readFileSync(file).toString('base64');
(async () => {
  const r = await fetch('https://api.deepseek.com/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + key },
    body: JSON.stringify({
      model: 'deepseek-v4-flash-vision-exp',
      max_tokens: 2000,
      reasoning_effort: 'none',
      messages: [{
        role: 'user',
        content: [
          { type: 'text', text: '请把这张图片里的所有文字完整、原样读出，特别是数字、金额、表格内容。用文字列表输出，不要漏任何数字。' },
          { type: 'image_url', image_url: { url: 'data:image/png;base64,' + b64 } }
        ]
      }]
    })
  });
  const j = await r.json();
  if (j.choices) console.log(j.choices[0].message.content);
  else console.log('错误:', JSON.stringify(j).slice(0, 400));
})();
" <图片路径>
```

要点：

- **`reasoning_effort: 'none'` 必须带。** 实测不带时，读一帧真实画面输出 718~922 token，
  其中 **664~877 是推理**，正文只剩三四十 —— 成本差 18 倍。关掉后每帧约 ¥0.0005。
  （`reasoning_effort: 'minimal'` **无效**，仍会烧掉 552 个推理 token；`thinking:
  {"type":"disabled"}` 也有效，等价。）
- 对数字/金额场景，提示词里明确「特别是数字、金额」效果最好
- 识别失败（模型限流/网络）：降级方案 C

---

## 方案 C（兜底）：本地 Tesseract

无网络、两个 API 都不可用时使用。

### Step 1: 依赖扫描（每次必做，5秒完成）

```bash
# Python 库检查
pip list 2>/dev/null | grep -iE "tesseract|easyocr|fitz|pymupdf|pillow|pdfplumber"

# Tesseract 二进制检查
ls "C:/Program Files/Tesseract-OCR/tesseract.exe" 2>/dev/null && echo "TESSERACT_OK"
where tesseract 2>/dev/null

# PyMuPDF 检查
python3 -c "import fitz; print('fitz OK')" 2>&1
```

### Step 2: 按可用工具选择方案（优先级从高到低）

| 工具 | 适用场景 | 关键点 |
|------|---------|--------|
| **PyMuPDF (fitz)** | PDF 页面渲染为图片 | `page.get_pixmap(dpi=200)` → `.save()` |
| **Tesseract + pytesseract** | 本地 OCR，中英混合 | 必须指定 `tesseract_cmd` 路径; `lang='chi_sim+eng'` |
| **EasyOCR** | 备选方案 | 需要 torch，Windows 可能 DLL 报错 |

### Step 3: 图像预处理（手机截屏场景）

```python
from PIL import Image, ImageEnhance
import numpy as np

img = Image.open('input.jpg')

# 1. 裁剪幻灯片区域（手机截屏中 PPT 只占中间 ~400px 高度）
# 2. 2倍放大（提高小字识别率）
img_big = img.resize((img.width*2, img.height*2), Image.LANCZOS)

# 3. 灰度 + 适度增强对比度（不要过曝）
img_gray = img_big.convert('L')
enhancer = ImageEnhance.Contrast(img_gray)
img_enh = enhancer.enhance(1.5)

# 4. 中度二值化（阈值 130，不要太激进）
arr = np.array(img_enh)
arr = np.where(arr > 130, 255, 0).astype(np.uint8)
img_bin = Image.fromarray(arr)
```

### Step 4: OCR 参数选择

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# PSM 模式：
# --psm 6  : PPT 幻灯片首选（统一文本块）
# --psm 11 : 思维导图/图表（稀疏文本）
# --psm 3  : 全自动（默认，效果不稳定）

text = pytesseract.image_to_string(img, lang='chi_sim+eng', config='--psm 6')
```

### Step 5: 结果保存（Windows GBK 终端兼容）

OCR 结果**必须写入文件**再读取，不能直接 print（GBK 编码会报错）：

```python
with open('ocr_result.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

### Step 6: 清理临时文件

任务完成后删除所有中间产物（`*.png`, `*.jpg` 等临时文件，保留原始文件）。

---

## 常见错误避免

| 错误 | 原因 | 解决 |
|------|------|------|
| 小米返回 `404 No endpoints found that support image input` | 用了 `mimo-v2.5-pro`（纯文本） | 换 `mimo-v2.5` |
| 小米返回 401 | key 取错地方了 | 必须从 cc-switch 库取，不是 settings.json |
| 小米返回 404 且是 HTML | 端点路径缺了 `/anthropic` | 用 `https://api.xiaomimimo.com/anthropic/v1/messages` |
| 视觉模型报 400/无 choices | key 无效或模型限流 | 换方案 B / C |
| DeepSeek 视觉账单偏高 | 没带 `reasoning_effort: 'none'` | 补上参数 |
| `TesseractNotFoundError` | 未安装或未配置路径 | 检查 `C:/Program Files/Tesseract-OCR/` |
| `UnicodeEncodeError: 'gbk'` | Windows 终端编码问题 | 结果写入文件，或 `sys.stdout.reconfigure(encoding='utf-8')` |
| EasyOCR torch DLL 报错 | Windows torch 兼容性问题 | 换用 Tesseract |
| OCR 结果乱码 | 二值化阈值太激进 | 阈值提高到 130-150 |
| 小字识别不了 | 图片分辨率太低 | 2倍放大后再 OCR，或改用方案 B |
