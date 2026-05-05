# -*- coding: utf-8 -*-
"""
QInspect AI — 90-Second Cinematic Promo Video
Story arc: Hook → Pain → Reveal → Dashboard → AI Inspection → Trace → Report → Results → CTA

Lessons applied from QScheduler:
  - page.mouse.move() after every page.evaluate() to force Chrome screencast frame flush
  - CSS animation disabled immediately after app load (headless Chrome throttles them)
  - at() function uses TRIM offset to align video frames with audio cues precisely
  - Nav gaps timed to cover app load + chart render
"""

import asyncio
import io
import re
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows (avoids cp932 UnicodeEncodeError with em-dash etc.)
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import imageio_ffmpeg

try:
    import edge_tts
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"], check=True)
    import edge_tts

OUTPUT_DIR = Path(__file__).parent / "video_output"
OUTPUT_DIR.mkdir(exist_ok=True)

WEBM_PATH = OUTPUT_DIR / "qinspect_promo_raw.webm"
MP4_PATH  = OUTPUT_DIR / "qinspect_promo_90s.mp4"
APP_URL   = "http://localhost:8001"
VOICE     = "ja-JP-NanamiNeural"
RATE      = "+8%"

# ─────────────────────────────────────────────────────────────
# NARRATION  — Story-driven, benefit-focused, emotionally engaging
# ─────────────────────────────────────────────────────────────
TTS_TEXTS = {
    "hook":    "製造現場の不良品見落とし、今日も起きていませんか。一件の見落としが、リコールを引き起こします。",
    "pain":    "疲れ、ムラ、見落とし。ひとによる目視検査の限界が、顧客信頼とブランドを傷つけます。",
    "reveal":  "QInspect AI。ディープラーニングが、ひとの目を超えた品質検査を実現します。",
    "dash":    "リアルタイム品質ダッシュボード。合格率97.3パーセント、AI精度99.6パーセント。ライン3の異常を即座に検知します。",
    "inspect": "AIスキャンが起動。CNNが欠陥を自動特定。気泡、クラックを99.6パーセントの精度で検出し、不合格を即座に判定します。",
    "trace":   "材料調達から出荷先まで完全追跡。不良発生の原因工程を秒単位で特定できます。",
    "report":  "AI予測で来月の不良率を先読み。設備リスクを事前検知し、重大不良を未然に防ぎます。",
    "results": "検査精度99.6パーセント。月間2万8千件を全品AI検査。不良流出リスクゼロ。QInspect AIが守る、あなたのブランド。",
    "cta":     "今すぐ無料デモをご体験ください。品質の未来を、今日から始めましょう。",
}

# Gap AFTER each section's TTS ends (nav/load time before next narration starts)
NAV_GAPS = {
    "hook":    1.0,   # local HTML switch (instant)
    "pain":    1.0,   # local HTML switch (instant)
    "reveal":  5.0,   # app network load + chart renders
    "dash":    3.5,   # switch to inspect tab
    "inspect": 1.2,   # switch to trace tab
    "trace":   1.2,   # switch to report tab
    "report":  0.8,   # switch to results HTML
    "results": 0.8,   # switch to CTA HTML
    "cta":     1.5,   # final buffer
}

SECTION_ORDER = ["hook", "pain", "reveal", "dash", "inspect", "trace", "report", "results", "cta"]

# ─────────────────────────────────────────────────────────────
# HTML SLIDE: HOOK  — The Problem Statement
# ─────────────────────────────────────────────────────────────
HOOK_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1280px;height:720px;overflow:hidden;}
body{background:#040810;font-family:-apple-system,'Segoe UI',Arial,sans-serif;
  display:flex;align-items:center;justify-content:center;}
.grain{position:fixed;inset:0;opacity:.04;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:200px 200px;pointer-events:none;}
.grid{position:fixed;inset:0;
  background-image:radial-gradient(circle,rgba(239,68,68,.06)1px,transparent 1px);
  background-size:32px 32px;}
.glow-r{position:fixed;top:40%;left:50%;transform:translate(-50%,-50%);
  width:700px;height:400px;
  background:radial-gradient(ellipse,rgba(239,68,68,.10)0%,transparent 65%);
  animation:breathe 4s ease-in-out infinite;}
@keyframes breathe{0%,100%{opacity:.7;transform:translate(-50%,-50%) scale(1);}
  50%{opacity:1;transform:translate(-50%,-50%) scale(1.08);}}
.content{position:relative;z-index:10;text-align:center;max-width:900px;padding:0 40px;}
.eyebrow{font-size:10px;font-weight:700;letter-spacing:.32em;text-transform:uppercase;
  color:rgba(239,68,68,.7);font-family:'Courier New',monospace;margin-bottom:28px;
  opacity:0;animation:up .5s ease .2s forwards;}
.q{font-size:58px;font-weight:900;color:#fff;line-height:1.1;letter-spacing:-.03em;
  margin-bottom:22px;opacity:0;animation:up .7s ease .5s forwards;
  text-shadow:0 2px 40px rgba(0,0,0,.6);}
.q .accent{color:#ef4444;}
.divider{width:60px;height:2px;background:linear-gradient(90deg,transparent,#ef4444,transparent);
  margin:0 auto 22px;opacity:0;animation:up .5s ease .9s forwards;}
.sub{font-size:22px;color:rgba(255,255,255,.5);font-weight:400;line-height:1.6;
  opacity:0;animation:up .6s ease 1.1s forwards;}
@keyframes up{from{opacity:0;transform:translateY(24px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="grain"></div>
<div class="grid"></div>
<div class="glow-r"></div>
<div class="content">
  <div class="eyebrow">Quality Inspection Crisis</div>
  <div class="q">製造現場の<span class="accent">不良品見落とし</span>、<br>今日も起きていませんか？</div>
  <div class="divider"></div>
  <div class="sub">一件の見落としが、<strong style="color:rgba(255,255,255,.8)">リコールを引き起こします。</strong></div>
</div>
</body></html>"""

# ─────────────────────────────────────────────────────────────
# HTML SLIDE: PAIN  — The Cost of Human Inspection
# ─────────────────────────────────────────────────────────────
PAIN_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1280px;height:720px;overflow:hidden;}
body{background:#060810;font-family:-apple-system,'Segoe UI',Arial,sans-serif;
  display:flex;align-items:center;justify-content:center;}
.grid{position:fixed;inset:0;
  background-image:radial-gradient(circle,rgba(239,68,68,.05)1px,transparent 1px);
  background-size:36px 36px;}
.glow-c{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  width:800px;height:500px;
  background:radial-gradient(ellipse,rgba(239,68,68,.09)0%,transparent 60%);}
.content{position:relative;z-index:10;width:860px;}
.header{text-align:center;margin-bottom:44px;
  opacity:0;animation:up .5s ease .2s forwards;}
.header-lbl{font-size:10px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;
  color:rgba(239,68,68,.7);font-family:'Courier New',monospace;}
.stats{display:flex;flex-direction:column;gap:0;}
.stat{display:flex;align-items:center;gap:28px;padding:22px 32px;
  border-bottom:1px solid rgba(255,255,255,.06);
  opacity:0;transform:translateX(-28px);}
.stat:last-of-type{border-bottom:none;}
.stat:nth-child(1){animation:slide .6s ease 0.9s forwards;}
.stat:nth-child(2){animation:slide .6s ease 3.1s forwards;}
.stat:nth-child(3){animation:slide .6s ease 5.3s forwards;}
.stat-icon{font-size:30px;flex-shrink:0;width:48px;text-align:center;}
.stat-body{flex:1;}
.stat-lbl{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:rgba(255,255,255,.35);margin-bottom:5px;}
.stat-num{font-size:42px;font-weight:900;font-family:'Courier New',monospace;
  letter-spacing:-.02em;line-height:1;}
.stat:nth-child(1) .stat-num{color:rgba(255,255,255,.8);}
.stat:nth-child(2) .stat-num{color:#f59e0b;}
.stat:nth-child(3) .stat-num{color:#ef4444;}
.stat-sub{font-size:13px;color:rgba(255,255,255,.32);margin-top:4px;}
.verdict{text-align:center;margin-top:36px;
  font-size:16px;color:rgba(255,255,255,.28);
  opacity:0;animation:up .5s ease 7.2s forwards;}
.verdict span{color:rgba(239,68,68,.8);font-weight:700;}
@keyframes up{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
@keyframes slide{from{opacity:0;transform:translateX(-28px);}to{opacity:1;transform:translateX(0);}}
</style></head><body>
<div class="grid"></div>
<div class="glow-c"></div>
<div class="content">
  <div class="header">
    <div class="header-lbl">人による目視検査の限界</div>
  </div>
  <div class="stats">
    <div class="stat">
      <div class="stat-icon">👁</div>
      <div class="stat-body">
        <div class="stat-lbl">見落とし率</div>
        <div class="stat-num">1〜3<span style="font-size:22px;color:rgba(255,255,255,.4)">%/日</span></div>
        <div class="stat-sub">疲労・集中力低下により午後は精度が最大30%低下</div>
      </div>
    </div>
    <div class="stat">
      <div class="stat-icon">⏰</div>
      <div class="stat-body">
        <div class="stat-lbl">検査コスト</div>
        <div class="stat-num">¥720<span style="font-size:22px;color:rgba(255,255,255,.4)">万/年</span></div>
        <div class="stat-sub">検査員3名 × 8時間/日 × 250日 の人件費</div>
      </div>
    </div>
    <div class="stat">
      <div class="stat-icon">🚨</div>
      <div class="stat-body">
        <div class="stat-lbl">リコール発生時の損害</div>
        <div class="stat-num">最大<span style="font-size:26px"> 数億円</span></div>
        <div class="stat-sub">製品回収 + 対応工数 + ブランド毀損 + 顧客離反</div>
      </div>
    </div>
  </div>
  <div class="verdict">この問題に、<span>根本的な解決策</span>があります。</div>
</div>
</body></html>"""

# ─────────────────────────────────────────────────────────────
# HTML SLIDE: REVEAL  — QInspect AI Solution
# ─────────────────────────────────────────────────────────────
REVEAL_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1280px;height:720px;overflow:hidden;}
body{background:#060a18;font-family:-apple-system,'Segoe UI',Arial,sans-serif;
  display:flex;align-items:center;justify-content:center;}
.grid{position:fixed;inset:0;
  background-image:radial-gradient(circle,rgba(239,68,68,.07)1px,transparent 1px);
  background-size:30px 30px;}
.glow1{position:fixed;top:50%;left:50%;transform:translate(-50%,-52%);
  width:800px;height:520px;
  background:radial-gradient(ellipse,rgba(220,38,38,.22)0%,transparent 55%);
  animation:pulse 3s ease-in-out infinite;}
.glow2{position:fixed;top:62%;right:10%;width:300px;height:300px;
  background:radial-gradient(ellipse,rgba(245,158,11,.12)0%,transparent 65%);}
@keyframes pulse{0%,100%{transform:translate(-50%,-52%) scale(1);opacity:.8;}
  50%{transform:translate(-50%,-52%) scale(1.06);opacity:1;}}
.content{position:relative;z-index:10;text-align:center;}
.logo-box{
  width:72px;height:72px;margin:0 auto 28px;
  background:linear-gradient(135deg,#dc2626,#f59e0b);
  border-radius:18px;display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 40px rgba(220,38,38,.5);
  opacity:0;animation:pop .6s cubic-bezier(.34,1.56,.64,1) .3s forwards;}
@keyframes pop{from{opacity:0;transform:scale(.4);}to{opacity:1;transform:scale(1);}}
.eyebrow{font-size:10px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;
  color:rgba(239,68,68,.75);font-family:'Courier New',monospace;
  margin-bottom:18px;opacity:0;animation:up .5s ease .7s forwards;}
h1{font-size:92px;font-weight:900;color:#fff;letter-spacing:-.05em;line-height:1;
  margin-bottom:20px;opacity:0;animation:up .7s ease .95s forwards;
  text-shadow:0 0 80px rgba(220,38,38,.35);}
h1 .ai{color:#fca5a5;}
.sub{font-size:22px;color:rgba(255,255,255,.42);font-weight:400;
  opacity:0;animation:up .6s ease 1.3s forwards;}
.tags{display:flex;align-items:center;gap:12px;justify-content:center;margin-top:28px;
  opacity:0;animation:up .5s ease 1.6s forwards;}
.tag{font-size:11px;font-family:'Courier New',monospace;font-weight:700;
  letter-spacing:.16em;padding:6px 16px;border-radius:6px;text-transform:uppercase;
  background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);color:rgba(239,68,68,.8);}
.dot{width:4px;height:4px;border-radius:50%;background:rgba(255,255,255,.2);}
@keyframes up{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="grid"></div>
<div class="glow1"></div>
<div class="glow2"></div>
<div class="content">
  <div class="logo-box">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"
      stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 18h8"/><path d="M3 22h18"/>
      <path d="M14 22a7 7 0 1 0 0-14h-1"/>
      <path d="M9 14h.01"/><path d="M9 6l.5-1 4.5 1.5-1.5 4.5L8 9.5"/>
      <path d="M9 6V3"/><circle cx="9" cy="6" r="1"/>
    </svg>
  </div>
  <div class="eyebrow">AI Visual Quality Inspection</div>
  <h1>QInspect <span class="ai">AI</span></h1>
  <div class="sub">ディープラーニングが、人の目を超える</div>
  <div class="tags">
    <div class="tag">AI画像検査</div>
    <div class="dot"></div>
    <div class="tag">トレーサビリティ</div>
    <div class="dot"></div>
    <div class="tag">品質予測</div>
  </div>
</div>
</body></html>"""

# ─────────────────────────────────────────────────────────────
# HTML SLIDE: RESULTS  — Proven Metrics
# ─────────────────────────────────────────────────────────────
RESULTS_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1280px;height:720px;overflow:hidden;}
body{background:#04100c;font-family:-apple-system,'Segoe UI',Arial,sans-serif;
  display:flex;align-items:center;justify-content:center;}
.grid{position:fixed;inset:0;
  background-image:radial-gradient(circle,rgba(16,185,129,.07)1px,transparent 1px);
  background-size:30px 30px;}
.glow{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  width:860px;height:560px;
  background:radial-gradient(ellipse,rgba(16,185,129,.14)0%,transparent 58%);
  animation:pulse 4s ease-in-out infinite;}
@keyframes pulse{0%,100%{opacity:.8;}50%{opacity:1;}}
.content{position:relative;z-index:10;text-align:center;width:1000px;}
.eyebrow{font-size:10px;font-weight:700;letter-spacing:.30em;text-transform:uppercase;
  color:rgba(16,185,129,.8);font-family:'Courier New',monospace;
  margin-bottom:44px;opacity:0;animation:up .5s ease .2s forwards;}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:2px;
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);
  border-radius:16px;overflow:hidden;}
.cell{padding:36px 44px;text-align:left;background:#04100c;
  position:relative;overflow:hidden;}
.cell::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.cell.green::before{background:linear-gradient(90deg,transparent,#10b981,transparent);}
.cell.blue::before{background:linear-gradient(90deg,transparent,#3b82f6,transparent);}
.cell.amber::before{background:linear-gradient(90deg,transparent,#f59e0b,transparent);}
.cell.red::before{background:linear-gradient(90deg,transparent,#ef4444,transparent);}
.cell:nth-child(1){animation:cellIn .6s ease .4s both;}
.cell:nth-child(2){animation:cellIn .6s ease .65s both;}
.cell:nth-child(3){animation:cellIn .6s ease .9s both;}
.cell:nth-child(4){animation:cellIn .6s ease 1.15s both;}
@keyframes cellIn{from{opacity:0;transform:scale(.96);}to{opacity:1;transform:scale(1);}}
.cell-lbl{font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(255,255,255,.3);margin-bottom:14px;}
.cell-val{font-size:62px;font-weight:900;font-family:'Courier New',monospace;
  letter-spacing:-.03em;line-height:1;margin-bottom:6px;}
.cell.green .cell-val{color:#10b981;}
.cell.blue  .cell-val{color:#3b82f6;}
.cell.amber .cell-val{color:#f59e0b;}
.cell.red   .cell-val{color:#ef4444;}
.cell-unit{font-size:22px;font-weight:500;opacity:.5;}
.cell-sub{font-size:12px;color:rgba(255,255,255,.3);margin-top:4px;}
@keyframes up{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="grid"></div>
<div class="glow"></div>
<div class="content">
  <div class="eyebrow">Proven Results — QInspect AI</div>
  <div class="grid2">
    <div class="cell green">
      <div class="cell-lbl">AI検査精度</div>
      <div class="cell-val">99.6<span class="cell-unit">%</span></div>
      <div class="cell-sub">DL-VGG v3.2 モデル / 全不良モード対応</div>
    </div>
    <div class="cell blue">
      <div class="cell-lbl">月間全品AI検査数</div>
      <div class="cell-val">28,412<span class="cell-unit">件</span></div>
      <div class="cell-sub">目視検査員ゼロ / 24時間365日稼働</div>
    </div>
    <div class="cell amber">
      <div class="cell-lbl">検査スピード</div>
      <div class="cell-val">0.3<span class="cell-unit">秒/件</span></div>
      <div class="cell-sub">人の目視検査（15分/件）比 → <strong style="color:#f59e0b">3,000倍</strong></div>
    </div>
    <div class="cell red">
      <div class="cell-lbl">不良流出リスク</div>
      <div class="cell-val">0<span class="cell-unit">件</span></div>
      <div class="cell-sub">完全トレーサビリティ × AI自動判定で実現</div>
    </div>
  </div>
</div>
</body></html>"""

# ─────────────────────────────────────────────────────────────
# HTML SLIDE: CTA  — Call to Action
# ─────────────────────────────────────────────────────────────
CTA_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1280px;height:720px;overflow:hidden;}
body{background:#060a18;font-family:-apple-system,'Segoe UI',Arial,sans-serif;
  display:flex;align-items:center;justify-content:center;}
.grid{position:fixed;inset:0;
  background-image:radial-gradient(circle,rgba(239,68,68,.06)1px,transparent 1px);
  background-size:32px 32px;}
.glow{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  width:820px;height:520px;
  background:radial-gradient(ellipse,rgba(220,38,38,.18)0%,transparent 58%);}
.content{position:relative;z-index:10;text-align:center;}
.logo-row{display:flex;align-items:center;justify-content:center;gap:14px;
  margin-bottom:40px;opacity:0;animation:up .6s ease .3s forwards;}
.logo-box{width:52px;height:52px;
  background:linear-gradient(135deg,#dc2626,#f59e0b);
  border-radius:13px;display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 24px rgba(220,38,38,.4);}
.logo-name{font-size:32px;font-weight:900;color:#fff;letter-spacing:-.03em;}
.logo-name span{color:#fca5a5;}
.headline{font-size:48px;font-weight:800;color:#fff;letter-spacing:-.03em;
  line-height:1.2;margin-bottom:32px;
  opacity:0;animation:up .7s ease .65s forwards;}
.headline .hl{color:#ef4444;}
.cta-box{display:inline-flex;align-items:center;gap:12px;
  background:linear-gradient(135deg,#991b1b,#dc2626);
  border-radius:14px;padding:18px 40px;margin-bottom:38px;
  box-shadow:0 8px 40px rgba(220,38,38,.4);
  opacity:0;animation:up .6s ease 1.0s forwards;}
.cta-text{font-size:22px;font-weight:800;color:#fff;letter-spacing:.01em;}
.url-wrap{opacity:0;animation:up .5s ease 1.35s forwards;}
.url-lbl{font-size:11px;color:rgba(255,255,255,.25);margin-bottom:8px;
  font-family:'Courier New',monospace;letter-spacing:.1em;}
.url{font-size:15px;color:rgba(255,255,255,.55);font-family:'Courier New',monospace;
  font-weight:700;letter-spacing:.02em;}
@keyframes up{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="grid"></div>
<div class="glow"></div>
<div class="content">
  <div class="logo-row">
    <div class="logo-box">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">
        <path d="M6 18h8"/><path d="M3 22h18"/>
        <path d="M14 22a7 7 0 1 0 0-14h-1"/>
        <path d="M9 6l.5-1 4.5 1.5-1.5 4.5L8 9.5"/>
        <path d="M9 6V3"/>
      </svg>
    </div>
    <div class="logo-name">QInspect <span>AI</span></div>
  </div>
  <div class="headline">製造の<span class="hl">品質革命</span>を、<br>今日から始めましょう。</div>
  <div class="cta-box">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5"
      stroke-linecap="round" stroke-linejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>
    <span class="cta-text">今すぐ無料デモを体験する</span>
  </div>
  <div class="url-wrap">
    <div class="url-lbl">Demo URL</div>
    <div class="url">quality-inspector-production.up.railway.app</div>
  </div>
</div>
</body></html>"""


# ─────────────────────────────────────────────────────────────
# PHASE 1: TTS GENERATION
# ─────────────────────────────────────────────────────────────

async def gen_tts(tmpdir: Path) -> dict:
    paths = {}
    for sid in SECTION_ORDER:
        out = tmpdir / f"tts_{sid}.mp3"
        print(f"  TTS [{sid}] generating...")
        communicate = edge_tts.Communicate(text=TTS_TEXTS[sid], voice=VOICE, rate=RATE)
        await communicate.save(str(out))
        paths[sid] = out
    return paths


def get_duration(path: Path, ffmpeg: str) -> float:
    result = subprocess.run(
        [ffmpeg, "-i", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 5.0


# ─────────────────────────────────────────────────────────────
# PHASE 2: BUILD NARRATION AUDIO TRACK
# ─────────────────────────────────────────────────────────────

def gen_silence(duration: float, out: Path, ffmpeg: str):
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono",
         "-t", f"{duration:.3f}",
         "-q:a", "2", str(out)],
        capture_output=True
    )


def build_narration(tmpdir: Path, tts_paths: dict, durations: dict, ffmpeg: str) -> Path:
    audio_files = []
    for sid in SECTION_ORDER:
        audio_files.append(tts_paths[sid])
        gap = NAV_GAPS[sid]
        if gap > 0:
            silence_path = tmpdir / f"silence_{sid}.mp3"
            gen_silence(gap, silence_path, ffmpeg)
            audio_files.append(silence_path)

    concat_file = tmpdir / "narration_concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for fp in audio_files:
            f.write(f"file '{str(fp).replace(chr(92), '/')}'\n")

    narration_path = tmpdir / "narration.mp3"
    result = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file),
         "-c:a", "libmp3lame", "-q:a", "2",
         str(narration_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ERROR building narration:", result.stderr[-500:])
        return None
    dur = get_duration(narration_path, ffmpeg)
    print(f"  Narration audio: {narration_path.name} ({dur:.1f}s)")
    return narration_path


# ─────────────────────────────────────────────────────────────
# PHASE 3: PLAYWRIGHT RECORDING
# Key technique: page.mouse.move(640,360) after every page.evaluate()
# forces Chrome to flush a new screencast frame immediately.
# Without this, headless Chrome defers painting until the next input event,
# causing page switches to appear 8+ seconds late in the video.
# ─────────────────────────────────────────────────────────────

def _nav_js(page_id: str) -> str:
    """JS to switch page without requiring a real DOM element argument."""
    tab_text = {
        "dash":    "ダッシュボード",
        "inspect": "AI画像検査",
        "trace":   "トレーサビリティ",
        "report":  "品質レポート",
    }
    txt = tab_text.get(page_id, "")
    return (
        f"(function(){{"
        f"document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));"
        f"document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));"
        f"document.getElementById('page-{page_id}').classList.add('active');"
        f"document.querySelectorAll('.nav-tab').forEach(t=>{{if(t.textContent.trim()==='{txt}')t.classList.add('active');}});"
        f"if('{page_id}'==='report'&&typeof initReportCharts==='function'&&!window.reportInit)initReportCharts();"
        f"}})()"
    )


async def record(tmpdir: Path, durations: dict):
    from playwright.async_api import async_playwright

    # Write HTML slides to temp files
    slides = {
        "hook":    tmpdir / "hook.html",
        "pain":    tmpdir / "pain.html",
        "reveal":  tmpdir / "reveal.html",
        "results": tmpdir / "results.html",
        "cta":     tmpdir / "cta.html",
    }
    slides["hook"].write_text(HOOK_HTML,    encoding="utf-8")
    slides["pain"].write_text(PAIN_HTML,    encoding="utf-8")
    slides["reveal"].write_text(REVEAL_HTML, encoding="utf-8")
    slides["results"].write_text(RESULTS_HTML, encoding="utf-8")
    slides["cta"].write_text(CTA_HTML,      encoding="utf-8")

    # Build cumulative audio timestamps
    ts = {}
    t = 0.0
    for sid in SECTION_ORDER:
        ts[f"{sid}_s"] = t
        t += durations[sid]
        ts[f"{sid}_e"] = t
        t += NAV_GAPS[sid]

    TRIM = 0.5  # FFmpeg -ss 0.5 trims startup flicker from video

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--allow-file-access-from-files",
                  "--disable-web-security"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720},
            device_scale_factor=1,
        )
        page = await context.new_page()

        # ── PRE-WARM: run concurrently with hook/pain/reveal slides ──
        # CRITICAL: t0 must be set BEFORE pre-warm starts, so the video
        # frame timeline starts from frame 0 (no gray blank during pre-warm).
        # We fire pre-warm as a background asyncio task; hook+pain+reveal
        # narration takes ~26s which is enough time for pre-warm (~15s) to
        # complete before we need to navigate to APP_URL.
        async def _prewarm():
            try:
                print("[Pre-warm] Loading app in background to warm browser cache...")
                bg = await context.new_page()
                await bg.goto(APP_URL, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(0.5)  # let JS fully settle
                await bg.close()
                print("[Pre-warm] Done — browser cache is hot.")
            except Exception as e:
                print(f"  Pre-warm warning: {e}")

        t0 = time.monotonic()
        prewarm_task = asyncio.create_task(_prewarm())

        async def at(audio_t: float):
            """Wait until video frame aligns with audio_t in narration track."""
            target = t0 + TRIM + audio_t
            wait = target - time.monotonic()
            if wait > 0.01:
                await asyncio.sleep(wait)
            elif wait < -0.5:
                print(f"  WARN: cue {audio_t:.1f}s missed by {-wait:.1f}s")

        # ── [1] HOOK CARD ────────────────────────────────────────
        print("[1] Hook — the problem")
        await page.goto(slides["hook"].as_uri())
        await page.mouse.move(640, 360)
        await at(ts["hook_e"])

        # ── [2] PAIN CARD ────────────────────────────────────────
        print("[2] Pain — cost of human inspection")
        await page.goto(slides["pain"].as_uri())
        await page.mouse.move(640, 360)
        await at(ts["pain_e"])

        # ── [3] REVEAL CARD — load app during reveal narration ───
        print("[3] Reveal — QInspect AI solution")
        await page.goto(slides["reveal"].as_uri())
        await page.mouse.move(640, 360)
        # Ensure pre-warm is done before navigating to app.
        # hook+pain+reveal ≈ 26s >> pre-warm time (~15s), so this is instant.
        await prewarm_task
        # Navigate to app after reveal narration.
        # domcontentloaded (not networkidle) = fast since cache is warm.
        await at(ts["reveal_e"])
        await page.goto(APP_URL, wait_until="domcontentloaded", timeout=15000)
        # Disable CSS page-switch animations (headless Chrome throttles them)
        await page.evaluate("""
            const s = document.createElement('style');
            s.textContent = '.page.active { animation: none !important; opacity: 1 !important; transform: none !important; }';
            document.head.appendChild(s);
        """)
        await page.evaluate("document.body.style.zoom = '0.85'")
        await page.mouse.move(640, 360)  # flush frame: app appears NOW in video

        # ── [4] DASHBOARD ────────────────────────────────────────
        await at(ts["dash_s"])
        await page.mouse.move(640, 360)  # second flush: ensures frame at exact dash start
        print("[4] Dashboard — hero card + KPIs + alerts")
        await asyncio.sleep(1.5)  # KPI skeleton → real values animate in
        await page.evaluate("window.scrollTo({top:180, behavior:'smooth'})")
        await asyncio.sleep(2.5)  # scroll down to show trend chart
        await page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
        await asyncio.sleep(1.5)
        # Switch to inspect tab during dash nav_gap
        await at(ts["dash_e"])
        await page.evaluate(_nav_js("inspect"))
        await page.mouse.move(640, 360)  # force frame flush — inspect page appears NOW

        # ── [5] AI INSPECTION ────────────────────────────────────
        await at(ts["inspect_s"])
        print("[5] AI Inspection — scan animation + verdict")
        # Immediately trigger inspection when narration starts
        await page.evaluate("document.getElementById('insp-btn').click()")
        await page.mouse.move(640, 360)  # force frame flush (scan line appears)
        await asyncio.sleep(2.2)  # scan animation: 60 frames × 33ms = ~2s
        await page.mouse.move(640, 360)  # keep flushing frames during animation
        await asyncio.sleep(0.8)  # detection boxes appear (2 × 400ms)
        await page.mouse.move(640, 360)
        await asyncio.sleep(0.7)  # verdict 不合格 overlay appears
        await page.mouse.move(640, 360)
        # Hold on verdict until narration ends, then switch to trace
        await at(ts["inspect_e"] - 0.5)
        await page.evaluate(_nav_js("trace"))
        await page.mouse.move(640, 360)  # force frame flush

        # ── [6] TRACEABILITY ─────────────────────────────────────
        await at(ts["trace_s"])
        print("[6] Traceability — timeline + genealogy")
        await asyncio.sleep(1.0)
        await page.evaluate("window.scrollTo({top:200, behavior:'smooth'})")
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
        await at(ts["trace_e"] - 0.5)
        await page.evaluate(_nav_js("report"))
        await page.mouse.move(640, 360)

        # ── [7] QUALITY REPORT ───────────────────────────────────
        await at(ts["report_s"])
        print("[7] Quality report — charts + AI prediction")
        await asyncio.sleep(1.5)  # chart.js renders
        await page.evaluate("window.scrollTo({top:220, behavior:'smooth'})")
        await asyncio.sleep(2.5)
        await page.evaluate("window.scrollTo({top:0, behavior:'smooth'})")
        await at(ts["report_e"])
        await page.goto(slides["results"].as_uri())
        await page.mouse.move(640, 360)

        # ── [8] RESULTS ──────────────────────────────────────────
        await at(ts["results_s"])
        print("[8] Results — proven metrics")
        await at(ts["results_e"])
        await page.goto(slides["cta"].as_uri())
        await page.mouse.move(640, 360)

        # ── [9] CTA ──────────────────────────────────────────────
        await at(ts["cta_s"])
        print("[9] CTA — call to action")
        await at(ts["cta_e"] + 1.5)  # +1.5s buffer after final word

        print("Recording complete.")
        await context.close()
        await browser.close()

    # Rename latest WebM
    webm_files = sorted(OUTPUT_DIR.glob("*.webm"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not webm_files:
        print("ERROR: No WebM generated")
        return False
    latest = webm_files[0]
    WEBM_PATH.unlink(missing_ok=True)
    latest.rename(WEBM_PATH)
    size_kb = WEBM_PATH.stat().st_size // 1024
    print(f"OK WebM: {WEBM_PATH} ({size_kb}KB)")
    return True


# ─────────────────────────────────────────────────────────────
# PHASE 4: ENCODE — cinematic grade + audio mix
# ─────────────────────────────────────────────────────────────

def encode(narration_path: Path, ffmpeg: str, total_dur: float) -> bool:
    # Cinematic grade:
    # curves: lift shadows slightly (dark HTML slides look good)
    # eq: modest contrast + saturation boost for app sections
    # vignette: draws focus to center
    # fade: smooth in/out
    fade_out_start = max(0, total_dur - 2.5)
    vf = (
        "curves=r='0 0.05 1 1':g='0 0.05 1 1':b='0 0.06 1 1',"
        "eq=saturation=1.2:contrast=1.05:brightness=0.01,"
        "vignette=PI/5,"
        f"fade=t=in:st=0:d=0.9,"
        f"fade=t=out:st={fade_out_start:.1f}:d=2.2"
    )
    cmd = [
        ffmpeg, "-y",
        "-ss", "0.5",
        "-i", str(WEBM_PATH),
        "-i", str(narration_path),
        "-t", str(int(total_dur) + 8),  # narration length + 8s buffer (was hardcoded 92, too short)
        "-vf", vf,
        "-c:v", "libx264",
        "-crf", "16",
        "-preset", "slow",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(MP4_PATH),
    ]
    print("Encoding with cinematic grade + audio...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr[-800:])
        return False
    size_mb = MP4_PATH.stat().st_size / 1_048_576
    print(f"OK MP4: {MP4_PATH} ({size_mb:.1f}MB)")
    return True


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

async def main():
    import tempfile
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    print("=" * 60)
    print("QInspect AI - 90-Second Cinematic Promo Video")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Phase 1: TTS
        print("\n[Phase 1] Generating Japanese TTS narration...")
        tts_paths = await gen_tts(tmpdir)

        print("[Phase 1] Measuring TTS durations...")
        durations = {}
        total_tts = 0.0
        total_silence = 0.0
        for sid in SECTION_ORDER:
            d = get_duration(tts_paths[sid], ffmpeg)
            durations[sid] = d
            total_tts += d
            total_silence += NAV_GAPS[sid]
            preview = TTS_TEXTS[sid][:28].replace("\n", " ")
            print(f"  {sid:<10}: {d:.1f}s  \"{preview}...\"")
        est_total = total_tts + total_silence
        print(f"  Total TTS: {total_tts:.1f}s | Total silence: {total_silence:.1f}s | Est. total: {est_total:.1f}s")

        # Phase 2: Narration audio
        print("\n[Phase 2] Building narration audio track...")
        narration_path = build_narration(tmpdir, tts_paths, durations, ffmpeg)
        if not narration_path:
            return

        # Phase 3: Record video
        print("\n[Phase 3] Recording Playwright video...")
        ok = await record(tmpdir, durations)
        if not ok:
            return

        # Phase 4: Encode
        print("\n[Phase 4] Encoding final MP4 (video + audio + cinematic grade)...")
        ok = encode(narration_path, ffmpeg, est_total)
        if not ok:
            return

    print("\n" + "=" * 60)
    print(f"DONE: {MP4_PATH}")
    print(f"Size: {MP4_PATH.stat().st_size / 1_048_576:.1f}MB")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
