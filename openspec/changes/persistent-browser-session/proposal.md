## Why

ผู้ใช้รายงานว่า session ของ gslide หลุดบ่อย — ต้อง `gslide auth login` ใหม่เรื่อยๆ ตรวจสอบแล้วพบ 2 root cause:

1. **"ไม่จำ" หลังเว้นนาน** — โค้ดโหลด `~/.gslide/storage_state.json` เข้า browser context ใหม่ทุกครั้ง แล้ว **ไม่เคยเขียน session กลับ**. Google หมุน cookie `__Secure-1PSIDTS` ตลอด แต่เราโยน token เก่าค้างกลับไปทุก run (core cookies ในไฟล์ยังไม่หมดอายุ — ปัญหาคือไม่ persist token ที่หมุน ไม่ใช่ cookie หมดอายุ)
2. **หลุดกลาง batch** — `gen` รัน headless + vanilla Chromium ไม่มี anti-detection → Google จับว่าเป็นบอทแล้ว revoke session กลางคัน เสีย slide ที่ทำค้างทั้ง batch

`storage_state.json` เป็น snapshot ตายตัว ไม่เหมาะกับ Google ที่หมุน cookie ต่อเนื่อง วิธีที่ยั่งยืนคือให้ Chromium จัดการ session เองผ่าน persistent profile (รับ Set-Cookie + หมุน token + persist ลงดิสก์ native) — แทนที่จะเขียน cookie management เองซึ่งเป็น technical debt

## What Changes

- เปลี่ยน session persistence จาก Playwright `storage_state.json` → **persistent browser profile** (`launch_persistent_context(user_data_dir=~/.gslide/profile)`)
- ลบฟังก์ชัน `save_session()` (persistent context persist เอง ไม่ต้อง save มือ)
- ใช้ **new headless mode (`--headless=new`)** สำหรับ gen/status — legacy headless shell โดน Google detect เด้งไป account chooser แม้ session ดี
- auto-detect inner profile (`Profile 1`) ที่ Google login shard ไป แล้วบันทึก marker `~/.gslide/active-profile` ส่งเป็น `--profile-directory` ทุก launch
- เพิ่ม anti-detection arg `--disable-blink-features=AutomationControlled` + explicit viewport (ไม่งั้นปุ่ม HMV ใน sidebar อยู่นอกจอ คลิกไม่ได้)
- dismiss onboarding modal ("Let's start creating") ก่อนคลิก HMV บน deck เปล่า
- เพิ่ม env var `GSLIDE_HEADED=1` บังคับ headed ทุกคำสั่ง (debug / กรณีโดน detect)
- **Mid-batch resilience**: เช็ค session ต้นทุกรอบใน batch loop, เพิ่ม `--start-from N` เพื่อ resume (presentation = checkpoint), screenshot รายแต่ละ slide ที่ fail, แสดง resume hint
- Migration: ผู้ใช้เดิมต้อง login ใหม่ 1 ครั้ง (แจ้งเตือนเมื่อพบไฟล์ storage_state.json เก่า)

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `browser-auth`: เปลี่ยน session persistence จาก storage state file เป็น persistent Chromium profile; login/status/logout ทำงานบน profile directory; เพิ่ม anti-detection arg และ `GSLIDE_HEADED` override
- `gen-batch`: เพิ่มการเช็ค session ต่อ slide, ตัวเลือก `--start-from` สำหรับ resume, screenshot ราย slide ที่ fail, resume hint เมื่อ batch หยุด

## Impact

- **No new dependencies** — ใช้ Playwright + Chromium เดิม (persistent context ใช้ chromium ตัวเดียวกัน)
- **Net code reduction** — ลบ `save_session()` + storage_state plumbing
- **Modified files**: `src/gslide/browser.py`, `src/gslide/auth.py`, `src/gslide/gen.py`, `src/gslide/cli.py`, `tests/test_auth.py`, `tests/test_browser.py`, `tests/test_gen.py`, `tests/test_cli.py`, `README.md`, `docs/project_brief.md`
- **Breaking for existing users**: ต้อง `gslide auth login` ใหม่ 1 ครั้ง (`storage_state.json` → `profile/`)
- **Accepted regression**: persistent profile ล็อก dir แบบ exclusive → รัน gslide 2 process พร้อมกันไม่ได้ (CLI ใช้แบบ sequential รับได้; ให้ error ชัดเมื่อ profile ถูกล็อก)
