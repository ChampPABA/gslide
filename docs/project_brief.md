# gslide — Project Brief

## Problem

NotebookLM สร้าง infographic และ slide deck ได้คุณภาพดี แต่มี **watermark** ทุกชิ้น ต้อง manual ลบก่อน import เข้า Google Slides ทำให้ workflow ช้าและไม่ scalable

## Solution

Python CLI tool ชื่อ `gslide` ที่ gen slides ตรงใน Google Slides ผ่านฟีเจอร์ "Help me visualize" (Gemini) — ไม่ผ่าน NotebookLM จึงไม่มี watermark

ปลายทางคือ **skill** ที่ Claude กับ user ร่วมกันสร้าง presentation ผ่าน CLI — ดูเหมือนคนทำ ไม่เหมือน AI template

## "Help me visualize" — 3 Tabs

| Tab | Gemini Model | Output | ใช้ใน Mode |
|-----|-------------|--------|-----------|
| **Slide** | Nano Banana Pro | slide สมบูรณ์ทั้งหน้า | Lazy |
| **Infographic** | Gemini 3 Pro + text rendering | infographic รายละเอียดมาก | Lazy |
| **Image** | Nano Banana Pro | รูปภาพ, logo, illustration | Craft |

## Why Browser Automation for Gemini Features

"Help me visualize" ไม่มี public API — ต้องใช้ browser automation เท่านั้น

จาก POC เมื่อ 16 มี.ค. 2026:

| แนวทาง | ผลลัพธ์ |
|---------|---------|
| HTTP API ตรง (`appsgenaiserver-pa.googleapis.com`) | ❌ ต้อง conversation history ~2MB, ต้อง OAuth2 |
| Python + SAPISIDHASH auth | ❌ 401 Unauthorized |
| Browser automation (agent-browser) | ✅ ทำงานได้ครบ |

**หมายเหตุ**: Google Slides REST API (`slides.googleapis.com`) ใช้ได้ปกติสำหรับสร้าง shapes, text, images — ใช้ไม่ได้แค่ Gemini gen features เท่านั้น

## 2 Generation Modes

### Lazy Mode (MVP — ทำก่อน)

ใช้ browser automation เรียก "Help me visualize" แล้ว insert เลย

- ใช้ **Slide tab** หรือ **Infographic tab** (detail มากกว่า)
- เร็ว (~45 วินาที/slide)
- ผลลัพธ์ดูเป็น AI-generated template
- **Status**: POC สำเร็จแล้ว, กำลังสร้าง CLI

### Craft Mode (ปลายทาง)

Claude เป็น **creative director** — วางแผน layout, กำหนด content strategy, เขียน prompt ทุกชิ้น

```
Claude (วางแผน + orchestrate)
  │
  ├── Google Slides API (CLI)
  │   → สร้าง text boxes, shapes, positioning, สี, font
  │   → จัด layout ทั้ง slide
  │
  └── Browser automation (headless)
      └── "Help me visualize" → Image tab
          → gen รูป, logo, icon, illustration
          → insert เป็น element ใน slide
  │
  ▼
Slide สมบูรณ์ — ดูเหมือนคนทำ
```

- **Google Slides API**: สร้าง structure (text, shapes, layout, styling)
- **Image tab**: gen visual elements เฉพาะจุด (รูป, logo, icon)
- **Claude**: ตัดสินใจทั้งหมด — layout, สี, content, prompt แต่ละ element
- ทำเป็น **skill** ที่ user กับ Claude ใช้ร่วมกันผ่าน CLI
- **Status**: 🔲 ยังไม่เริ่ม

## Auth Pattern

Pattern เหมือน notebooklm-py — login ครั้งเดียว ใช้ซ้ำได้จนหมดอายุ

### Login Flow (เรียนรู้จาก POC 16-17 มี.ค. 2026)

```
1. เปิด agent-browser แบบ headed mode (ต้องเห็นหน้าจอ)
   $ agent-browser --headed

2. Navigate ไป Google Slides presentation URL
   > go https://docs.google.com/presentation/d/[ID]/edit

3. Google จะ redirect ไป login page
   → User login ด้วย Google account ปกติ (manual)
   → รอจน redirect กลับมาที่ presentation สำเร็จ

4. Export cookies ทั้งหมดจาก browser session
   > cookies get --json
   → ได้ JSON array ของ cookies ทุก domain

5. Save เป็น storage state file
   → เก็บไว้ที่ ~/.gslide/storage_state.json
```

### สิ่งที่เรียนรู้จาก POC

- **ต้องใช้ `cookies get --json`** — ได้ httpOnly cookies ครบ (SID, HSID, SSID, SAPISID)
- **ห้ามใช้ `document.cookie`** — ได้แค่ non-httpOnly cookies ซึ่งขาด cookies สำคัญสำหรับ auth
- **ต้องเก็บ cookies หลาย domain**: `.google.com`, `docs.google.com`, `accounts.google.com`
- **Headed mode จำเป็นสำหรับ login**: Google บล็อก headless browser ตอน login (bot detection)
- **หลัง login แล้ว headless ใช้ได้**: โหลด cookies กลับเข้า browser → เข้า Google Slides ได้โดยไม่ต้อง login ซ้ำ
- **SAPISIDHASH**: ต้อง gen จาก SAPISID cookie + timestamp + origin URL ตาม formula `SHA1(timestamp + " " + SAPISID + " " + origin)` — ใช้สำหรับ API calls ที่ต้องการ auth header

## Workflow Steps — Lazy Mode (Browser Automation)

```
1. Open presentation URL with --state (headless)
2. Navigate to last slide (Press End)
3. Click "Help me visualize" button
4. Switch to tab ที่ต้องการ (Slide / Infographic)
5. Type prompt in textbox
6. Click "Create" → wait 30-50 seconds
7. Click generated preview
8. Click "Insert on new slide"
9. Repeat 3-8 for each slide
```

## Prompt Engineering

### Infographic mind map style
```
Landscape 16:9 mind map infographic. Clean white background,
minimal and professional design for university submission.
Topic: [TOPIC]. Center: [CENTER NODE] with [ICON].
Branch 1: [CATEGORY] — [details]
Branch 2: [CATEGORY] — [details]
Branch 3: [CATEGORY] — [details]
Use soft muted colors. Simple flat professional icons.
Thin clean connecting lines. All text in Thai.
```

### Neo Brutalism style
```
Landscape 16:9 infographic in Neo Brutalism style with bold
black borders. Title: [TITLE]. Show [N] items as blocks
with thick borders. Each block has Thai text label and icon.
Dark background with red/yellow/orange accents.
```

## Known Gotchas

- **Insert vs Replace**: Slide แรกจะเห็น "Insert as new slide" แต่ slide ถัดไปจะเห็น "Replace" → ต้องกด "More options" → "Insert on new slide"
- **Blank first page**: Insert จะสร้าง blank slide แรกที่ต้องลบ
- **CSS selector trick**: snapshot ไม่เห็น generated image เป็น ref → ใช้ `click "[aria-label^='Create infographic']"` แทน
- **Generation time**: ~30-50 วินาทีต่อ slide
- **No existing skill**: ค้นหาแล้วไม่มี skill สำหรับ "Help me visualize" — ต้องสร้างเอง

## Tech Stack

- **Language**: Python (stdlib + Playwright)
- **Browser Engine**: agent-browser (Playwright-based)
- **Auth**: Google session cookies via storage state
- **Gemini Gen**: "Help me visualize" ผ่าน browser automation
- **Slides Structure** (craft mode): Google Slides REST API
- **Orchestration** (craft mode): Claude — วางแผน, ตัดสินใจ, เขียน prompt

## References

- [notebooklm-py](https://github.com/teng-lin/notebooklm-py) — pattern reference สำหรับ CLI design, auth
- [Google Slides API Guide](https://developers.google.com/workspace/slides/api/guides/add-shape) — สำหรับ craft mode
- [Help me visualize docs](https://support.google.com/docs/answer/16443280) — 3 tabs: Slide, Infographic, Image
