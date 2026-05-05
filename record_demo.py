# -*- coding: utf-8 -*-
# QInspect AI - X post demo video recorder
# Playwright -> WebM -> MP4  (~30 seconds)

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

OUTPUT_DIR = Path(__file__).parent / "video_output"
OUTPUT_DIR.mkdir(exist_ok=True)

WEBM_PATH = OUTPUT_DIR / "qinspect_raw.webm"
MP4_PATH  = OUTPUT_DIR / "qinspect_x_post_30s.mp4"
APP_URL   = "https://quality-inspector-production.up.railway.app"


async def record():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720},
            device_scale_factor=1,
        )
        page = await context.new_page()

        # ── 1. Dashboard ───────────────────────────────────────────
        print("[1] Opening app - Dashboard")
        await page.goto(APP_URL)
        await page.wait_for_timeout(2000)   # 初期レンダリング待機
        # 75%ズームで画面下部を見切れなくする
        await page.evaluate("document.body.style.zoom = '0.75'")
        await page.wait_for_timeout(1500)   # KPI counters + charts animate

        # ── 2. AI Image Inspection - Product A (FAIL) ─────────────
        print("[2] Navigate to AI Inspection tab")
        await page.click("text=AI画像検査")
        await page.wait_for_timeout(800)    # page transition + canvas draw

        print("[3] Run inspection on Product A (ADC-X200) - FAIL case")
        await page.click("#insp-btn")
        await page.wait_for_timeout(6000)   # scan 2s + 2 defect boxes + verdict + view

        # ── 3. AI Image Inspection - Product C (PASS) ─────────────
        print("[4] Select Product C (INJ-S100) - PASS case")
        await page.click("text=INJ-S100")
        await page.wait_for_timeout(600)

        print("[5] Run inspection on Product C - PASS case")
        await page.click("#insp-btn")
        await page.wait_for_timeout(4500)   # scan 2s + no boxes + pass verdict + view

        # ── 4. Traceability ────────────────────────────────────────
        print("[6] Navigate to Traceability")
        await page.click("text=トレーサビリティ")
        await page.wait_for_timeout(600)

        print("[7] Show traceability timeline")
        await page.wait_for_timeout(3800)   # read timeline + genealogy

        # ── 5. Quality Report ──────────────────────────────────────
        print("[8] Navigate to Quality Report")
        await page.click("text=品質レポート")
        await page.wait_for_timeout(600)

        print("[9] Show report charts")
        await page.wait_for_timeout(3200)   # charts render + KPI cards

        # Scroll down to show Pareto chart
        print("[10] Scroll to Pareto chart")
        await page.evaluate("window.scrollTo({top: 500, behavior: 'smooth'})")
        await page.wait_for_timeout(3000)   # final view

        # ── Done ───────────────────────────────────────────────────
        await context.close()
        await browser.close()

    # Find the latest WebM file saved by Playwright
    webm_files = sorted(OUTPUT_DIR.glob("*.webm"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not webm_files:
        print("ERROR: WebM file not found")
        sys.exit(1)
    latest_webm = webm_files[0]
    if latest_webm != WEBM_PATH:
        WEBM_PATH.unlink(missing_ok=True)  # 既存ファイルを先に削除（Windows対応）
        latest_webm.rename(WEBM_PATH)
    print(f"OK WebM saved: {WEBM_PATH}")


def convert_to_mp4():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    duration = WEBM_PATH  # check actual duration first

    print("Converting to MP4 (H.264, high quality)...")
    cmd = [
        ffmpeg,
        "-y",
        "-ss", "3",            # skip ~3s browser/startup overhead
        "-i", str(WEBM_PATH),
        "-t", "30",            # cap at 30 seconds
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-an",                 # no audio
        "-movflags", "+faststart",
        str(MP4_PATH),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: ffmpeg failed")
        print(result.stderr[-2000:])
        sys.exit(1)
    size_mb = MP4_PATH.stat().st_size / 1024 / 1024
    print(f"OK MP4 saved: {MP4_PATH}")
    print(f"   Size: {size_mb:.1f} MB")


async def main():
    print("=" * 55)
    print("QInspect AI - Demo Video Recorder (target: ~30s)")
    print("=" * 55)
    await record()
    convert_to_mp4()
    print()
    print("=" * 55)
    print(f"DONE: {MP4_PATH.resolve()}")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
