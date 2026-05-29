import streamlit as st


def apply_dark_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ql-bg: #0b1020;
            --ql-panel: #111827;
            --ql-panel-soft: #172033;
            --ql-border: #283247;
            --ql-text: #e5eefc;
            --ql-muted: #94a3b8;
            --ql-accent: #22d3ee;
            --ql-accent-2: #a3e635;
            --ql-danger: #fb7185;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 211, 238, 0.11), transparent 34rem),
                linear-gradient(135deg, #08111f 0%, #101827 45%, #121826 100%);
            color: var(--ql-text);
        }

        [data-testid="stSidebar"] {
            background: rgba(7, 13, 25, 0.96);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }

        [data-testid="stSidebar"] * {
            color: var(--ql-text);
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 2.1rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        h1 {
            font-size: 2.35rem;
            font-weight: 760;
        }

        h2 {
            font-size: 1.3rem;
            margin-top: 1.2rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 8px;
            padding: 1rem;
        }

        div[data-testid="stForm"] {
            background: rgba(17, 24, 39, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            padding: 1.1rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.54);
        }

        .ql-record {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.68);
            padding: 1rem 1.05rem;
            margin-bottom: 0.75rem;
        }

        .ql-record-title {
            color: var(--ql-text);
            font-size: 1.02rem;
            font-weight: 720;
            margin-bottom: 0.25rem;
        }

        .ql-meta {
            color: var(--ql-muted);
            font-size: 0.82rem;
            margin-bottom: 0.45rem;
        }

        .ql-tag {
            display: inline-block;
            border: 1px solid rgba(34, 211, 238, 0.26);
            border-radius: 999px;
            color: #cffafe;
            background: rgba(8, 145, 178, 0.16);
            padding: 0.12rem 0.48rem;
            margin: 0.12rem 0.2rem 0.12rem 0;
            font-size: 0.76rem;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {
            border-radius: 8px;
            border: 1px solid rgba(34, 211, 238, 0.30);
            background: linear-gradient(135deg, #0891b2 0%, #0f766e 100%);
            color: white;
            font-weight: 700;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: rgba(163, 230, 53, 0.56);
            color: white;
        }

        input, textarea, [data-baseweb="select"] {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
