#!/usr/bin/env python3
r"""
generate_cv.py — build James Bray's 2-page PDF CV from the site content.

Renders a light-mode, print-tuned HTML CV (same design language as the
website, quieter) and prints it to PDF via headless Chrome. Fonts are
inlined as base64 so the PDF is self-contained and portable.

    python tools/generate_cv.py

WHAT TO EDIT
------------
Everything you'd want to tweak lives in the CONFIG block below:
  * CONTACT            — name, title, contact links, summary line
  * EXPERIENCE / EDUCATION / PROJECTS — set "on": False to drop an entry,
                         or trim its "bullets" list to shorten it
  * PROFICIENCIES      — the three skill columns
  * SECTIONS           — which sections appear, their order, and (optionally)
                         which start on a fresh page (page_break)

Only entries with "on": True are included, so you can keep the full history
here and switch pieces in/out per application. Aim to keep it to 2 pages —
the script prints the page count after building.

Needs: Chrome/Chromium (for print-to-pdf). No Python packages required.
"""

import base64
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "content" / "fonts"
OUT_PDF = ROOT / "content" / "CV.pdf"          # the CV page's download button points here

# ============================================================
# CONFIG — edit me
# ============================================================

CONTACT = {
    "name":  "James Bray",
    "kicker": "Aerospace R&D — UAV Systems",
    "title": "R&D Contractor",
    "summary": (
        "Aerospace MEng graduate specialising in UAV system software, with a broad base "
        "of projects across firmware, controls and simulation. I drop into cross-disciplinary "
        "teams, move fast between system design and hands-on build, and ship working results."
    ),
    "links": [
        # (label, shown-text, href) — href None renders as plain text
        ("Email",    "jamesbray03@protonmail.com", "mailto:jamesbray03@protonmail.com"),
        ("Web",      "jamesbray.uk",               "https://www.jamesbray.uk/"),
        ("LinkedIn", "linkedin.com/in/jamesbray03", "https://www.linkedin.com/in/jamesbray03/"),
    ],
}

EXPERIENCE = [
    {
        "on": True,
        "role": "Integration Engineer",
        "org": "XPRIZE AURA",
        "org_url": "https://aura-xprize.com/",
        "date": "Sep 2025 – Jun 2026",
        "bullets": [
            "Deployed in Alaska to manage integration of computer-vision systems into the tech stack",
            "Engineered a novel thermal detection refinement method to localise fires with 1 m accuracy",
            "Profiled the system architecture to identify and mitigate critical network bottlenecks",
            "Ran rapid hardware-in-the-loop testing cycles across a 38 h non-stop development sprint",
        ],
    },
    {
        "on": True,
        "role": "Propulsion Avionics Engineer",
        "org": "Sunride",
        "org_url": "https://www.sunride.space/",
        "date": "Sep 2024 – May 2026",
        "bullets": [
            "Designed avionic systems for the university's first liquid rocket engine test stand",
            "Used LabJack DAQ systems to interface sensors and actuators for precise control",
            "Built a Simulink fluid model with PID control to regulate fuel and oxidiser flow",
            "Implemented fault detection and safety protocols for engine test procedures",
        ],
    },
    {
        "on": True,
        "role": "Assistant Project Engineer",
        "org": "AMRC",
        "org_url": "https://www.amrc.co.uk/",
        "date": "Jul 2024 – Oct 2024",
        "bullets": [
            "Designed and manufactured a £4,000 partial-discharge testing cell for 20 kV motor coils",
            "Coordinated with 6 suppliers to source components for manufacturing",
            "Managed deliverables, mitigated risks and produced supporting documentation",
            "Used Ansys FEA to evaluate geometries for slinky-stator manufacture and a robot end effector",
        ],
    },
    {
        "on": True,
        "role": "Catalogue Executive",
        "org": "MinsterFB",
        "org_url": "https://www.minsterfb.com/",
        "date": "Jul 2022 – Oct 2022",
        "bullets": [
            "Created and optimised product listings for maximum engagement and profitability",
            "Built an automated product-name generator in Excel from supplier data",
            "Designed enhanced graphical content for 5 brands using Canva and Inkscape",
        ],
    },
]

EDUCATION = [
    {
        "on": True,
        "role": "Aerospace Engineering MEng",
        "org": "University of Sheffield",
        "org_url": "https://www.sheffield.ac.uk/",
        "date": "Sep 2022 – May 2026",
        "lines": [
            "Five-year integrated master's, final year — first-class. Avionics-focused: electronic "
            "systems and control theory applied to aerospace.",
        ],
        # optional compact highlight of strongest modules; set to [] to hide
        "bullets": [
            "Dissertation: \u2018Risk-Aware Multi-UAV Search Strategies for Large-Scale Wildfire Detection\u2019",
            "Favourite modules: State-Space Control Design (92%), Multisensor Decision Systems (87%), "
            "Aircraft Dynamics & Control (85%), Real-Time Embedded Systems (79%)",
        ],
    },
    {
        "on": True,
        "role": "A-Levels & GCSEs",
        "org": "George Spencer Academy",
        "org_url": "https://georgespencer.org.uk/",
        "date": "Sep 2015 – Jul 2022",
        "lines": [],
        "bullets": [
            "A-Levels: A*AAA in Maths, Further Maths, Computer Science, Physics",
            "GCSEs: four grade 9s (Maths, Biology, Chemistry, Physics); grade 7–8 in Computer Science, "
            "D&T, Geography and English",
        ],
    },
]

# Optional Projects section — trim/toggle to taste. Off by default to protect
# the 2-page budget; flip "on": True to include an entry.
PROJECTS = [
    {
        "on": False,
        "role": "VTOL Quadplane — Design, Build & Test",
        "org": "",
        "org_url": None,
        "date": "Sep 2024 – May 2025",
        "bullets": [
            "Led design and integration of the full avionics system for a modular VTOL UAV",
            "Built an ironbird avionics testbed to verify systems before final integration",
            "Optimised cooling by externally mounting ESCs and positioning for airflow",
        ],
    },
    {
        "on": False,
        "role": "Lightweight Quadcopter — Design, Build & Test",
        "org": "",
        "org_url": None,
        "date": "Sep 2023 – May 2024",
        "bullets": [
            "Won the contract for the lightest flying drone across a cohort of 31 teams",
            "Led the control team, tuning flight behaviour via PID in BetaFlight",
            "Used topology optimisation to maximise the frame's strength-to-weight ratio",
        ],
    },
]

PROFICIENCIES = {
    "on": True,
    "columns": {
        "Technical": [
            "Avionics & control systems",
            "Algorithm development",
            "Embedded / real-time firmware",
            "Advanced manufacturing",
        ],
        "Software": [
            "Python, C, C#",
            "MATLAB & Simulink",
            "Git & version control",
            "Unity, Blender",
        ],
        "Strengths": [
            "Cross-disciplinary R&D",
            "System optimisation",
            "Analytical problem-solving",
            "Leadership & collaboration",
        ],
    },
}

# Section order, headings, and page control.
#   key      -> which content block to render
#   page_break: True forces the section to start on a new page
SECTIONS = [
    {"key": "experience",    "no": "01", "title": "Experience",    "page_break": False},
    {"key": "education",     "no": "02", "title": "Education",     "page_break": False},
    {"key": "proficiencies", "no": "03", "title": "Proficiencies", "page_break": False},
    {"key": "projects",      "no": "04", "title": "Selected Projects", "page_break": True},
]

# Page geometry / density
PAGE = {
    "size": "A4",
    "margin": "12mm 13mm 11mm",   # top, sides, bottom
    "base_pt": 9.6,               # body font size
}
# ============================================================


def font_face(family: str, filename: str, weight: str = "normal") -> str:
    data = (FONT_DIR / filename).read_bytes()
    b64 = base64.b64encode(data).decode()
    return (
        f"@font-face{{font-family:'{family}';"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
        f"font-weight:{weight};font-style:normal;font-display:swap;}}"
    )


def link(text: str, href) -> str:
    if not href:
        return escape(text)
    return f'<a href="{escape(href)}">{escape(text)}</a>'


def render_entry(e: dict) -> str:
    org = ""
    if e.get("org"):
        org = f' <span class="org">— {link(e["org"], e.get("org_url"))}</span>'
    bullets = ""
    lines = "".join(f"<p>{escape(l)}</p>" for l in e.get("lines", []))
    if e.get("bullets"):
        items = "".join(f"<li>{escape(b)}</li>" for b in e["bullets"])
        bullets = f"<ul>{items}</ul>"
    return (
        '<div class="entry">'
        '<div class="entry-head">'
        f'<h3>{escape(e["role"])}{org}</h3>'
        f'<span class="date">{escape(e["date"])}</span>'
        "</div>"
        f"{lines}{bullets}"
        "</div>"
    )


def render_proficiencies(p: dict) -> str:
    cols = ""
    for name, items in p["columns"].items():
        li = "".join(f"<li>{escape(i)}</li>" for i in items)
        cols += f'<div class="prof-col"><h4>{escape(name)}</h4><ul>{li}</ul></div>'
    return f'<div class="prof-grid">{cols}</div>'


def render_section(sec: dict) -> str:
    key = sec["key"]
    if key == "experience":
        body = "".join(render_entry(e) for e in EXPERIENCE if e.get("on"))
    elif key == "education":
        body = "".join(render_entry(e) for e in EDUCATION if e.get("on"))
    elif key == "projects":
        body = "".join(render_entry(e) for e in PROJECTS if e.get("on"))
    elif key == "proficiencies":
        if not PROFICIENCIES.get("on"):
            return ""
        body = render_proficiencies(PROFICIENCIES)
    else:
        return ""
    if not body.strip():
        return ""
    cls = "section" + (" page-break" if sec.get("page_break") else "")
    return (
        f'<section class="{cls}">'
        '<div class="section-head">'

        f'<h2>{escape(sec["title"])}</h2>'
        "</div>"
        f"{body}"
        "</section>"
    )


def render_header() -> str:
    links = "".join(
        f'<span class="contact-item">{link(text, href)}</span>'
        for _, text, href in CONTACT["links"]
    )
    return (
        '<header class="cv-header">'
        f'<h1>{escape(CONTACT["name"])}</h1>'
        f'<p class="role">{escape(CONTACT["title"])}</p>'
        f'<p class="summary">{escape(CONTACT["summary"])}</p>'
        f'<p class="contact">{links}</p>'
        "</header>"
    )


def build_html() -> str:
    faces = "".join([
        font_face("Space Grotesk", "SpaceGrotesk.woff2", "300 700"),
        font_face("HarmonyOS", "HarmonyOS.woff2"),
        font_face("JetBrains Mono", "JetBrainsMono.woff2", "100 800"),
    ])
    sections = "".join(render_section(s) for s in SECTIONS)
    css = CSS.replace("__MARGIN__", PAGE["margin"]) \
             .replace("__SIZE__", PAGE["size"]) \
             .replace("__BASE__", str(PAGE["base_pt"]))
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<style>{faces}{css}</style></head><body>"
        f"{render_header()}{sections}"
        "</body></html>"
    )


# Light-mode, print-tuned. Tokens mirror the site's light theme but quieter.
CSS = r"""
:root{
  --ink:#161b22; --dim:#3f4855; --faint:#707a88;
  --line:#dfe3ea; --accent:#0d72d8;
  --font-body:'HarmonyOS','Segoe UI',system-ui,sans-serif;
  --font-display:'Space Grotesk','HarmonyOS',sans-serif;
  --font-mono:'JetBrains Mono',Consolas,monospace;
}
@page{ size:__SIZE__; margin:__MARGIN__; }
*{ box-sizing:border-box; }
html,body{ margin:0; padding:0; }
body{
  font-family:var(--font-body); color:var(--ink);
  font-size:__BASE__pt; line-height:1.4;
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
a{ color:var(--accent); text-decoration:none; }
h1,h2,h3,h4{ font-family:var(--font-display); margin:0; letter-spacing:-0.01em; color:var(--ink); }

/* kicker: mono accent tick + label */
.kicker{
  display:inline-flex; align-items:center; gap:.5em;
  font-family:var(--font-mono); font-size:6.6pt; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase; color:var(--accent);
}
.kicker::before{ content:''; width:1.3em; height:1px; background:var(--accent); opacity:.7; }

/* header */
.cv-header{ padding-bottom:.55rem; margin-bottom:.4rem; border-bottom:1px solid var(--line); }
.cv-header h1{ font-size:23pt; font-weight:600; margin:.18rem 0 .05rem; }
.cv-header .role{
  font-family:var(--font-mono); font-size:8.4pt; letter-spacing:.06em;
  color:var(--dim); margin:0 0 .35rem; text-transform:uppercase;
}
.cv-header .summary{ color:var(--dim); margin:.15rem 0 .45rem; max-width:52em; }
.cv-header .contact{
  font-family:var(--font-mono); font-size:7.8pt; letter-spacing:.02em;
  color:var(--dim); margin:0;
  display:flex; justify-content:space-between;
}

/* sections */
.section{ margin-top:.7rem; }
.section .section-head{ margin-bottom:.3rem; }
.section.page-break{ break-before:page; }

/* entries: hairline-separated, never split across a page */
.entry{ break-inside:avoid; padding:.28rem 0 .3rem; border-top:1px solid var(--line); }
.section .section-head + .entry{ border-top:none; }
.entry-head{ display:flex; justify-content:space-between; align-items:baseline; gap:1rem; }
.entry-head h3{ font-size:10.5pt; font-weight:600; }
.entry-head .org{ font-family:var(--font-body); font-weight:400; color:var(--dim); font-size:9.6pt; }
.entry-head .org a{ font-family:var(--font-display); }
.entry .date{
  flex-shrink:0; font-family:var(--font-mono); font-size:7.4pt; font-weight:500;
  letter-spacing:.06em; text-transform:uppercase; color:var(--faint);
}
.entry p{ margin:.1rem 0; color:var(--dim); }
.entry ul{ margin:.12rem 0 0; padding-left:1.6rem; }
.entry li{ margin:.03rem 0; color:var(--dim); }
.entry li::marker{ color:var(--faint); }

/* keep a heading glued to its first entry */
.section-head{ break-after:avoid; }
.section .section-head h2{ font-size:14pt; font-weight:600; margin:.1rem 0 .25rem; padding-bottom:.25rem; border-bottom:1.5px solid var(--line); }

/* proficiencies: three tight columns */
.prof-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem; break-inside:avoid; }
.prof-col h4{
  font-family:var(--font-mono); font-size:6.8pt; font-weight:600; letter-spacing:.12em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .2rem;
  padding-bottom:.2rem; border-bottom:1px solid var(--line);
}
.prof-col ul{ margin:.25rem 0 0; padding-left:1.5rem; }
.prof-col li{ margin:.05rem 0; color:var(--dim); }
.prof-col li::marker{ color:var(--faint); }
"""


def find_chrome() -> str:
    for c in ("chrome", "chromium", "msedge"):
        p = shutil.which(c)
        if p:
            return p
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    sys.exit("Chrome/Chromium/Edge not found — install one or add it to PATH.")


def page_count(pdf: Path) -> int | None:
    """Best-effort page count without extra deps.

    Counts /Type /Page objects but excludes the /Type /Pages tree node
    (which contains '/Page' as a substring).
    """
    import re
    try:
        data = pdf.read_bytes()
        return len(re.findall(rb"/Type\s*/Page(?![s])", data))
    except Exception:
        return None


def main():
    html = build_html()
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        html_path = tmp / "cv.html"
        html_path.write_text(html, encoding="utf-8")
        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={OUT_PDF}",
            f"--user-data-dir={tmp / 'profile'}",
            html_path.as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if not OUT_PDF.exists():
            sys.exit(f"Chrome failed to produce PDF:\n{res.stderr}")
    pages = page_count(OUT_PDF)
    tag = f"{pages} page(s)" if pages else "page count unknown"
    print(f"Wrote {OUT_PDF.relative_to(ROOT).as_posix()}  ({tag})")
    if pages and pages > 2:
        print("  ⚠ over 2 pages — drop an entry (\"on\": False) or trim bullets.")


if __name__ == "__main__":
    main()
