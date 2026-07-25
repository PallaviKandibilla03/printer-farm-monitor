import time
import boto3
import pandas as pd
import streamlit as st
from datetime import datetime
from aws_config import (
    AWS_REGION,
    STATUS_TABLE,
    EVENTS_TABLE,
)

# ---------------------------------------------------
# PAGE
# ---------------------------------------------------

st.set_page_config(
    page_title="Printer Farm Monitor",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------
# Palette: deep slate base, cool indigo accent, restrained status colors.
BG          = "#0a0e17"
PANEL       = "#111826"
PANEL_2     = "#161f30"
BORDER      = "#232d40"
TEXT        = "#e6eaf2"
TEXT_MUTED  = "#8b96ab"
ACCENT      = "#6366f1"   # indigo — primary brand accent
ACCENT_2    = "#22d3ee"   # cyan — secondary accent for gradients
OK          = "#22c55e"
WARN        = "#f59e0b"
HIGH        = "#f43f5e"
NONE_SEV    = "#3b82f6"

SEVERITY_COLOR = {
    "NONE": NONE_SEV,
    "LOW": OK,
    "MEDIUM": WARN,
    "HIGH": HIGH,
}

# ---------------------------------------------------
# ICONS (inline SVG, stroke-based, single accent color)
# ---------------------------------------------------

def icon(name, color=ACCENT, size=20):
    paths = {
        "printer": '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
        "warning": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h.79a4.5 4.5 0 1 1 0 9Z"/>',
        "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
        "pulse": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
        "check": '<path d="M20 6 9 17l-5-5"/>',
    }
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
        viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round">{paths.get(name, "")}</svg>'''


def badge(label, color):
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'background:{color}1f;color:{color};border:1px solid {color}55;'
        f'padding:3px 10px;border-radius:999px;font-size:12.5px;font-weight:600;'
        f'letter-spacing:.02em;">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:{color};'
        f'display:inline-block;"></span>{label}</span>'
    )


# ---------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] {{
    background:{BG};
    color:{TEXT};
    font-family:'Inter', sans-serif;
}}

.block-container{{
    padding-top:1.6rem;
    padding-bottom:3rem;
    max-width:1400px;
}}

section[data-testid="stSidebar"] {{
    background:{PANEL};
    border-right:1px solid {BORDER};
}}

hr {{
    border-color:{BORDER} !important;
    margin:1.6rem 0 !important;
}}

/* ---------- Title bar ---------- */
.topbar {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:18px 24px;
    background:linear-gradient(135deg, {PANEL} 0%, {PANEL_2} 100%);
    border:1px solid {BORDER};
    border-radius:16px;
    margin-bottom:24px;
}}
.topbar-left {{
    display:flex;
    align-items:center;
    gap:14px;
}}
.logo-badge {{
    width:42px;
    height:42px;
    border-radius:11px;
    background:linear-gradient(135deg, {ACCENT} 0%, {ACCENT_2} 100%);
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:0 4px 14px {ACCENT}44;
}}
.topbar-title {{
    font-size:21px;
    font-weight:800;
    letter-spacing:-.01em;
    line-height:1.15;
}}
.topbar-subtitle {{
    font-size:13px;
    color:{TEXT_MUTED};
    font-weight:500;
    margin-top:1px;
}}
.topbar-right {{
    display:flex;
    align-items:center;
    gap:10px;
    font-size:13px;
    color:{TEXT_MUTED};
    font-family:'JetBrains Mono', monospace;
}}
.live-dot {{
    width:8px;
    height:8px;
    border-radius:50%;
    background:{OK};
    box-shadow:0 0 0 3px {OK}22;
    display:inline-block;
    animation:pulse 2s infinite;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; }}
    50% {{ opacity:.4; }}
}}

/* ---------- KPI cards ---------- */
.metric-card{{
    background:linear-gradient(155deg, {PANEL_2} 0%, {PANEL} 100%);
    border:1px solid {BORDER};
    border-radius:16px;
    padding:20px 22px;
    box-shadow:0 4px 16px rgba(0,0,0,.28);
    position:relative;
    overflow:hidden;
}}
.metric-card::before{{
    content:"";
    position:absolute;
    top:0; left:0; right:0;
    height:3px;
    background:var(--accent-line, {ACCENT});
}}
.metric-icon{{
    opacity:.85;
    margin-bottom:10px;
}}
.metric-title{{
    color:{TEXT_MUTED};
    font-size:12.5px;
    font-weight:700;
    letter-spacing:.06em;
    text-transform:uppercase;
}}
.metric-value{{
    font-size:38px;
    font-weight:800;
    margin-top:6px;
    letter-spacing:-.02em;
}}

/* ---------- Printer cards ---------- */
.printer-card{{
    background:{PANEL_2};
    border:1px solid {BORDER};
    border-radius:14px;
    padding:18px 20px;
    border-left:4px solid {OK};
    margin-bottom:15px;
    transition:transform .15s ease;
}}
.printer-card.alert{{
    border-left:4px solid {HIGH};
}}
.printer-title{{
    font-size:17px;
    font-weight:700;
    display:flex;
    align-items:center;
    gap:8px;
}}
.printer-row{{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-top:10px;
    font-size:13px;
}}
.printer-row .label{{
    color:{TEXT_MUTED};
    font-weight:500;
}}
.printer-updated{{
    margin-top:12px;
    font-size:11.5px;
    color:{TEXT_MUTED};
    font-family:'JetBrains Mono', monospace;
}}

.section-title{{
    margin-top:8px;
    margin-bottom:14px;
    font-size:20px;
    font-weight:800;
    display:flex;
    align-items:center;
    gap:10px;
    letter-spacing:-.01em;
}}

/* ---------- Rounded native containers (charts / tables) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"]{{
    border-radius:16px !important;
    border-color:{BORDER} !important;
    background:{PANEL_2};
}}

div[data-testid="stDataFrame"]{{
    border-radius:12px;
    overflow:hidden;
}}

/* ---------- Footer ---------- */
.footer{{
    text-align:center;
    padding:20px;
    color:{TEXT_MUTED};
    font-size:12.5px;
    letter-spacing:.02em;
}}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# AWS
# ---------------------------------------------------

session = boto3.Session(

    region_name=AWS_REGION
)

dynamodb = session.resource("dynamodb")

status_table = dynamodb.Table(STATUS_TABLE)
events_table = dynamodb.Table(EVENTS_TABLE)

status_items = status_table.scan().get("Items", [])
event_items = events_table.scan().get("Items", [])

status_df = pd.DataFrame(status_items)
events_df = pd.DataFrame(event_items)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.markdown(
    f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        <div class="logo-badge" style="width:34px;height:34px;">{icon("printer", "#fff", 18)}</div>
        <div style="font-weight:800;font-size:16px;">Printer Farm</div>
    </div>''',
    unsafe_allow_html=True,
)

st.sidebar.markdown(badge("System Online", OK), unsafe_allow_html=True)
st.sidebar.write("")

st.sidebar.metric("Region", AWS_REGION)
st.sidebar.metric("Printers", len(status_df))
st.sidebar.metric("Events", len(event_items))
st.sidebar.metric("Last Refresh", datetime.now().strftime("%H:%M:%S"))

if st.sidebar.button("Refresh now", use_container_width=True):
    st.rerun()

# ---------------------------------------------------
# TOP BAR
# ---------------------------------------------------

st.markdown(
    f'''
    <div class="topbar">
        <div class="topbar-left">
            <div class="logo-badge">{icon("printer", "#0a0e17", 22)}</div>
            <div>
                <div class="topbar-title">Printer Farm Monitoring</div>
                <div class="topbar-subtitle">Edge Computing Platform · Fleet Overview</div>
            </div>
        </div>
        <div class="topbar-right">
            <span class="live-dot"></span> LIVE &nbsp;·&nbsp; {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# KPIs
# ---------------------------------------------------

healthy = 0
alerts = 0

if not status_df.empty:
    healthy = (status_df["status"] == "HEALTHY").sum()
    alerts = len(status_df) - healthy

kpi_defs = [
    ("printer", ACCENT, "TOTAL PRINTERS", len(status_df)),
    ("check", OK, "HEALTHY", healthy),
    ("warning", HIGH, "ACTIVE ALERTS", alerts),
    ("pulse", ACCENT_2, "TOTAL EVENTS", len(event_items)),
]

cols = st.columns(4)
for col, (ic, color, title, value) in zip(cols, kpi_defs):
    with col:
        st.markdown(
            f'''
            <div class="metric-card" style="--accent-line:{color};">
                <div class="metric-icon">{icon(ic, color, 22)}</div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------
# PRINTER FARM
# ---------------------------------------------------

st.markdown(
    f'<div class="section-title">{icon("printer", ACCENT)} Current Printer Fleet</div>',
    unsafe_allow_html=True,
)

if not status_df.empty:
    status_df = status_df.sort_values("printer_id")
    cols = st.columns(3)

    for index, (_, row) in enumerate(status_df.iterrows()):
        is_healthy = row["status"] == "HEALTHY"
        card_class = "printer-card" if is_healthy else "printer-card alert"
        status_color = OK if is_healthy else HIGH
        sev_color = SEVERITY_COLOR.get(row["severity"], TEXT_MUTED)

        with cols[index % 3]:
            st.markdown(
                f'''
                <div class="{card_class}">
                    <div class="printer-title">
                        {icon("printer", status_color, 17)} {row["printer_id"]}
                    </div>
                    <div class="printer-row">
                        <span class="label">Status</span>
                        {badge(row["status"], status_color)}
                    </div>
                    <div class="printer-row">
                        <span class="label">Severity</span>
                        {badge(row["severity"], sev_color)}
                    </div>
                    <div class="printer-updated">Updated {row["last_update"]}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
else:
    st.info("No printer data available.")

st.markdown("---")

# ---------------------------------------------------
# ACTIVE ALERTS
# ---------------------------------------------------

st.markdown(
    f'<div class="section-title">{icon("warning", HIGH)} Current Active Alerts</div>',
    unsafe_allow_html=True,
)

if not status_df.empty:
    active = status_df[status_df["status"] != "HEALTHY"].copy()

    if active.empty:
        st.success("No active alerts.")
    else:
        active = active[["printer_id", "status", "severity", "last_update"]]
        with st.container(border=True):
            st.dataframe(active, hide_index=True, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------
# RECENT EVENTS
# ---------------------------------------------------

# ---------------------------------------------------
# RECENT EVENTS
# ---------------------------------------------------

st.markdown(
    f'<div class="section-title">{icon("pulse", ACCENT_2)} Latest Events</div>',
    unsafe_allow_html=True,
)

if not events_df.empty:

    recent = events_df.copy()

    recent["timestamp"] = pd.to_datetime(
        recent["timestamp"],
        errors="coerce"
    )

    recent = (
        recent
        .dropna(subset=["timestamp"])
        .sort_values("timestamp", ascending=False)
        .reset_index(drop=True)
    )

    columns = [
        "timestamp",
        "printer_id",
        "event",
        "type",
        "severity",
        "message",
    ]

    columns = [c for c in columns if c in recent.columns]

    with st.container(border=True):
        st.dataframe(
            recent[columns],
            hide_index=True,
            use_container_width=True,
        )

else:
    st.info("No recent events.")

# ---------------------------------------------------
# DASHBOARD ANALYTICS
# ---------------------------------------------------

st.markdown(
    f'<div class="section-title">{icon("database", ACCENT)} Dashboard Analytics</div>',
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("**Alerts by Severity**")
        if not events_df.empty and "severity" in events_df.columns:
            severity = (
                events_df["severity"]
                .value_counts()
                .rename_axis("Severity")
                .reset_index(name="Count")
                .set_index("Severity")
            )
            st.bar_chart(severity, height=250, use_container_width=True)
        else:
            st.info("No alert data available.")

with right:
    with st.container(border=True):
        st.markdown("**Events by Printer**")
        if not events_df.empty and "printer_id" in events_df.columns:
            printer_counts = (
                events_df["printer_id"]
                .value_counts()
                .sort_index()
                .rename_axis("Printer")
                .reset_index(name="Events")
                .set_index("Printer")
            )
            st.bar_chart(printer_counts, height=250, use_container_width=True)
        else:
            st.info("No printer event data.")

st.markdown("---")

# ---------------------------------------------------
# SYSTEM INFORMATION
# ---------------------------------------------------

st.markdown(
    f'<div class="section-title">{icon("cloud", ACCENT_2)} System Information</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)

with c1:
    with st.container(border=True):
        st.markdown(f"""
{icon("database", ACCENT, 16)} &nbsp;**AWS Region:** `{AWS_REGION}`

{icon("database", ACCENT, 16)} &nbsp;**Status Table:** `{STATUS_TABLE}`

{icon("database", ACCENT, 16)} &nbsp;**Events Table:** `{EVENTS_TABLE}`
""", unsafe_allow_html=True)

with c2:
    with st.container(border=True):
        st.markdown(badge("SYSTEM ONLINE", OK), unsafe_allow_html=True)
        st.markdown(f"""

**Last Refresh:** `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`

{icon("cloud", ACCENT_2, 16)} &nbsp;Cloud services connected
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown(
    '''
    <div class="footer">
        Printer Farm Monitoring System<br>
        Edge Computing · FastAPI · Amazon SQS · AWS Lambda · DynamoDB · Streamlit
    </div>
    ''',
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# AUTO REFRESH (native Streamlit rerun, no JS reload)
# ---------------------------------------------------

REFRESH_SECONDS = 5
time.sleep(REFRESH_SECONDS)
st.rerun()