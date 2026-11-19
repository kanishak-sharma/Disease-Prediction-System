"""Look-and-feel helpers: CSS, hero banner, cards, footer."""
from __future__ import annotations

import html

import streamlit as st

from core.knowledge import DISCLAIMER

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; }
#MainMenu, footer {visibility: hidden; height: 0;}
[data-testid="stHeader"] { background: rgba(255,255,255,.92); }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }
h1, h2, h3 { letter-spacing: -0.02em; color: #12332f; }
.hero { background: linear-gradient(135deg, #0b5d56 0%, #0f766e 45%, #14a39a 100%); color: #fff;
  border-radius: 24px; padding: 2.6rem 2.4rem; margin-bottom: 1.6rem; position: relative; overflow: hidden;
  box-shadow: 0 18px 40px -18px rgba(15,118,110,.6); }
.hero:after { content:""; position:absolute; right:-80px; top:-80px; width:320px; height:320px; border-radius:50%;
  background: radial-gradient(circle, rgba(255,255,255,.22), rgba(255,255,255,0) 70%); }
.hero h1 { color:#fff; font-size: 2.5rem; font-weight: 800; margin: 0 0 .5rem 0; line-height: 1.12; }
.hero p { font-size: 1.1rem; opacity: .93; max-width: 700px; margin: 0 0 1rem 0; }
.pill { display:inline-block; background: rgba(255,255,255,.17); border:1px solid rgba(255,255,255,.3); color:#fff;
  padding: .28rem .8rem; border-radius: 999px; font-size: .82rem; margin: 0 .4rem .4rem 0; font-weight: 500; }
.page-head { margin-bottom: 1.2rem; }
.page-head h1 { font-size: 2rem; margin-bottom: .2rem; font-weight: 800; }
.page-head p { color: #5b6b69; margin: 0; font-size: 1.02rem; }
.card { background:#fff; border:1px solid #e3ecea; border-radius: 18px; padding: 1.2rem 1.3rem; height: 100%;
  box-shadow: 0 1px 2px rgba(16,24,40,.04); transition: transform .15s ease, box-shadow .15s ease; }
.card:hover { transform: translateY(-2px); box-shadow: 0 12px 24px -12px rgba(16,24,40,.18); }
.card .ico { font-size: 1.9rem; line-height: 1; margin-bottom: .55rem; }
.card h4 { margin: 0 0 .25rem 0; font-size: 1.08rem; font-weight: 700; color:#12332f; }
.card p { margin: 0; color: #5b6b69; font-size: .92rem; line-height: 1.45; }
.card .meta { margin-top: .7rem; font-size: .78rem; color:#7b8a88; }
.stat { background: #f2f8f7; border-radius: 16px; padding: 1rem 1.2rem; text-align: center; }
.stat b { display:block; font-size: 1.9rem; color:#0f766e; font-weight: 800; line-height: 1.1; }
.stat span { font-size: .85rem; color:#5b6b69; }
.badge { display:inline-block; padding:.15rem .6rem; border-radius: 999px; font-size:.72rem; font-weight:700; letter-spacing:.02em; }
.badge.new { background:#e0f2ff; color:#0b69a3; } .badge.team { background:#e6f6ec; color:#1f7a3d; }
.badge.exp { background:#fff1d6; color:#9a6200; }
.result-card { border-radius: 20px; padding: 1.4rem 1.5rem; border: 1px solid; }
.result-card.low { background:#effaf2; border-color:#b8e5c6; } .result-card.moderate { background:#fff8e6; border-color:#f3dc9a; }
.result-card.high { background:#fff0f0; border-color:#f5bcbc; }
.result-card h2 { margin: 0 0 .3rem 0; font-size: 1.6rem; }
.result-card p { margin: .25rem 0; color:#334; }
.flag { border-left: 5px solid; border-radius: 10px; padding: .7rem 1rem; margin-bottom: .6rem; background:#fff; border-top:1px solid #eef2f1; border-right:1px solid #eef2f1; border-bottom:1px solid #eef2f1;}
.flag.watch { border-left-color:#f59f00; } .flag.see { border-left-color:#f76707; } .flag.urgent { border-left-color:#e03131; background:#fff5f5; }
.flag small { display:block; font-weight:700; text-transform:uppercase; letter-spacing:.05em; font-size:.68rem; color:#667; }
.step { display:flex; gap:.9rem; align-items:flex-start; }
.step .n { flex:0 0 38px; height:38px; border-radius:50%; background:#0f766e; color:#fff; font-weight:800;
  display:flex; align-items:center; justify-content:center; }
.tip { background:#f2f8f7; border-radius:14px; padding:.9rem 1rem; height:100%; }
.tip b { color:#0f766e; display:block; margin-bottom:.15rem; }
.tip span { font-size:.88rem; color:#4b5b59; }
.footer { margin-top: 3rem; padding: 1.2rem 0 .4rem 0; border-top: 1px solid #e3ecea; text-align:center; color:#7b8a88; font-size:.84rem; }
.disclaimer { background:#fff8e6; border:1px solid #f3dc9a; border-radius:14px; padding:.8rem 1rem; font-size:.88rem; color:#6b4e00; }
div[data-testid="stMetric"] { background:#f2f8f7; border-radius:14px; padding:.8rem 1rem; }
.stButton > button, .stDownloadButton > button { border-radius: 12px; font-weight: 600; }
button[kind="primary"] { background:#0f766e; border-color:#0f766e; }
@media (max-width: 640px) { .hero { padding: 1.6rem 1.2rem; } .hero h1 { font-size: 1.8rem; } }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def esc(s) -> str:
    return html.escape(str(s))


def hero(title: str, subtitle: str, pills: list[str] | None = None) -> None:
    pill_html = "".join(f'<span class="pill">{esc(p)}</span>' for p in (pills or []))
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p>{pill_html}</div>', unsafe_allow_html=True)


def page_head(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-head"><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div>', unsafe_allow_html=True)


def stat(value: str, label: str) -> str:
    return f'<div class="stat"><b>{esc(value)}</b><span>{esc(label)}</span></div>'


def status_badge(status: str) -> str:
    cls = {"New": "new", "Team model": "team", "Experimental": "exp"}.get(status, "new")
    return f'<span class="badge {cls}">{esc(status)}</span>'


def disease_card(cfg: dict) -> str:
    return (f'<div class="card"><div class="ico">{cfg["emoji"]}</div><h4>{esc(cfg["name"])} {status_badge(cfg["status"])}</h4>'
            f'<p>{esc(cfg["tagline"])}</p><div class="meta">{esc(cfg["model_name"])} · {esc(cfg["data_source"].split("(")[0].strip())}</div></div>')


def disclaimer() -> None:
    st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER.replace("**", "")}</div>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown('<div class="footer">Multi-Disease Prediction System · Systematic Machine Learning course project · '
                'Built with Python, scikit-learn, Plotly and Streamlit<br>For education only. Not medical advice.</div>',
                unsafe_allow_html=True)
