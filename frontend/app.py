import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = os.getenv(
    "API_URL",
    "http://backend:8000" if os.path.exists("/.dockerenv") else "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="Bank Churn Prediction",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - WHITE / PREMIUM / ENGINEERING-GRADE
# ============================================================================

st.markdown(
    """
<style>
/* -------------------- Palette / Base -------------------- */
:root{
  --paper: #ffffff;
  --paper2: #f6f7fb;
  --paper3: #eef1f7;

  --ink: #0f172a;
  --muted: rgba(15,23,42,0.65);
  --muted2: rgba(15,23,42,0.50);
  --line: rgba(15,23,42,0.10);

  --accent: #2563eb;
  --accent2: #1d4ed8;

  --ok: #16a34a;
  --warn: #d97706;
  --bad: #dc2626;

  --shadow1: 0 10px 22px rgba(15,23,42,0.08);
  --shadow2: 0 14px 32px rgba(15,23,42,0.10);
  --radius-xl: 18px;
  --radius-lg: 14px;
  --radius-md: 12px;
}

html, body, [class*="css"]{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
  color: var(--ink);
}

/* -------------------- App background -------------------- */
.stApp{
  background: var(--paper);
}

/* Main container sizing */
.main .block-container{
  padding-top: 1.4rem;
  padding-bottom: 2.2rem;
  max-width: 1280px;
}

/* Remove excessive default padding in some blocks */
div[data-testid="stVerticalBlock"] > div:has(> div.stMarkdown){
  margin-top: 0.25rem;
}

/* -------------------- Sidebar -------------------- */
[data-testid="stSidebar"]{
  background: linear-gradient(180deg, var(--paper) 0%, var(--paper2) 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] *{
  color: var(--ink) !important;
}
[data-testid="stSidebar"] hr{
  border-color: var(--line);
}

/* Sidebar radio group */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 0.55rem 0.65rem;
  box-shadow: 0 8px 18px rgba(15,23,42,0.06);
}
[data-testid="stSidebar"] .stRadio label{
  font-weight: 650;
  letter-spacing: 0.2px;
}

/* -------------------- Headings / text -------------------- */
h1, h2, h3, h4{
  color: var(--ink) !important;
  letter-spacing: -0.2px;
}
h1{
  font-weight: 840 !important;
  line-height: 1.12;
}
h2{ font-weight: 780 !important; }
h3{ font-weight: 720 !important; }

.caption-muted{
  color: var(--muted2);
  font-size: 13px;
  line-height: 1.4;
}

/* -------------------- Premium surfaces -------------------- */
.paper{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  padding: 1.25rem 1.25rem;
  box-shadow: var(--shadow1);
}

.hero{
  background:
    radial-gradient(1000px 320px at 20% 0%, rgba(37,99,235,0.10), transparent 55%),
    radial-gradient(850px 300px at 80% 0%, rgba(29,78,216,0.08), transparent 55%),
    linear-gradient(180deg, var(--paper) 0%, var(--paper2) 100%);
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  padding: 1.35rem 1.35rem;
  box-shadow: var(--shadow2);
}

.grid-card{
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 1.05rem 1.05rem;
  box-shadow: 0 10px 20px rgba(15,23,42,0.07);
  transition: transform 140ms ease, box-shadow 140ms ease;
}
.grid-card:hover{
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(15,23,42,0.10);
}

/* KPI */
.kpi{
  display: grid;
  gap: 0.18rem;
}
.kpi .label{
  color: rgba(15,23,42,0.55);
  font-size: 12px;
  letter-spacing: 0.28px;
  text-transform: uppercase;
}
.kpi .value{
  font-size: 26px;
  font-weight: 820;
  color: var(--ink);
  letter-spacing: -0.35px;
}
.kpi .sub{
  font-size: 12.5px;
  color: rgba(15,23,42,0.55);
}

/* Thin divider */
.rule{
  height: 1px;
  background: var(--line);
  margin: 1rem 0 1rem 0;
}

/* -------------------- Buttons -------------------- */
.stButton > button{
  width: 100%;
  border-radius: var(--radius-md);
  height: 3.1em;
  background: linear-gradient(180deg, var(--accent) 0%, var(--accent2) 100%);
  color: white;
  font-weight: 720;
  font-size: 15px;
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 10px 20px rgba(37,99,235,0.18);
  transition: transform 140ms ease, box-shadow 140ms ease, filter 140ms ease;
}
.stButton > button:hover{
  filter: brightness(1.02);
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(37,99,235,0.22);
}

/* Download button style aligns with primary button */
[data-testid="stDownloadButton"] > button{
  width: 100%;
  border-radius: var(--radius-md);
  height: 3.1em;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: white;
  font-weight: 700;
  font-size: 15px;
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 10px 20px rgba(15,23,42,0.16);
}

/* -------------------- Inputs -------------------- */
.stNumberInput input,
.stTextInput input,
.stSelectbox select{
  border-radius: var(--radius-md) !important;
  border: 1px solid rgba(15,23,42,0.12) !important;
  background: var(--paper) !important;
  transition: box-shadow 140ms ease, border 140ms ease;
}
.stNumberInput input:focus,
.stTextInput input:focus,
.stSelectbox select:focus{
  border: 1px solid rgba(37,99,235,0.45) !important;
  box-shadow: 0 0 0 4px rgba(37,99,235,0.12) !important;
}

/* -------------------- Alerts / DF / Progress -------------------- */
.stAlert{ border-radius: var(--radius-lg); }
[data-testid="stDataFrame"]{
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
}
.stProgress > div > div > div > div{
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 100%);
}

/* -------------------- Prediction banner -------------------- */
.prediction-banner{
  border-radius: var(--radius-xl);
  padding: 1.1rem 1.2rem;
  border: 1px solid rgba(15,23,42,0.10);
  background:
    radial-gradient(900px 260px at 20% 0%, rgba(37,99,235,0.10), transparent 60%),
    linear-gradient(180deg, var(--paper) 0%, var(--paper2) 100%);
  box-shadow: var(--shadow2);
}
.prediction-banner .title{
  font-size: 15px;
  font-weight: 760;
  color: var(--ink);
  letter-spacing: 0.2px;
}
.prediction-banner .risk{
  margin-top: 0.35rem;
  font-size: 28px;
  font-weight: 860;
  letter-spacing: -0.45px;
}
.risk-high{ color: var(--bad); }
.risk-med{ color: var(--warn); }
.risk-low{ color: var(--ok); }

/* -------------------- Plotly container polish -------------------- */
.js-plotly-plot, .plotly, .plot-container{
  border-radius: var(--radius-lg);
}

/* Reduce top gap from default markdown anchors */
[data-testid="stMarkdownContainer"] p{
  margin-bottom: 0.35rem;
}
</style>
""",
    unsafe_allow_html=True
)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.85rem 0.85rem 0.55rem 0.85rem;">
          <div style="font-weight: 860; font-size: 18px; letter-spacing: -0.2px;">Churn AI</div>
          <div class="caption-muted" style="margin-top: 2px;">MLOps Frontend • Real-time prediction</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        ["Dashboard", "Prediction", "Batch Analysis", "Analytics"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("**System status**")

    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            if status == "healthy":
                st.success("API online")
                st.info("Model loaded")
            else:
                st.warning(f"Status: {status}")
        else:
            st.error("API error")
    except Exception as e:
        st.error("API offline")
        st.caption(f"Error: {str(e)[:70]}")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="caption-muted" style="padding: 0.25rem 0.85rem 0.85rem 0.85rem;">
          MLOps Project<br/>
          Churn Prediction System<br/>
          v2.0.0
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================

if page == "Dashboard":
    st.markdown(
        """
        <div class="hero">
          <div style="display:flex; align-items:flex-end; justify-content:space-between; gap: 16px; flex-wrap: wrap;">
            <div>
              <h1 style="margin: 0 0 0.35rem 0;">Bank Churn Prediction</h1>
              <div style="color: rgba(15,23,42,0.68); font-size: 15.5px;">
                Production-grade churn scoring interface for your MLOps pipeline
              </div>
            </div>
            <div style="color: rgba(15,23,42,0.55); font-size: 13px; text-align:right;">
              API: <b>{api}</b>
            </div>
          </div>
        </div>
        """.format(api=API_URL),
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Model quality</div>
                <div class="value" style="font-size: 22px;">Reliable</div>
                <div class="sub">Stable performance across evaluation runs</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Latency</div>
                <div class="value" style="font-size: 22px;">Real-time</div>
                <div class="sub">Optimized endpoint for interactive scoring</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Monitoring</div>
                <div class="value" style="font-size: 22px;">Batch-ready</div>
                <div class="sub">Exports + probability distributions</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    try:
        response = requests.get(f"{API_URL}/model-info", timeout=3)
        if response.status_code == 200:
            info = response.json()
            metrics = info.get("metrics", {})

            st.markdown("<div class='paper'>", unsafe_allow_html=True)
            st.markdown("<h2 style='margin: 0.1rem 0 0.9rem 0;'>Model information</h2>", unsafe_allow_html=True)

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(
                    f"""
                    <div class="kpi">
                      <div class="label">Model</div>
                      <div class="value" style="font-size: 18px;">{info.get('model_name', 'N/A').split('(')[0]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with k2:
                st.markdown(
                    f"""
                    <div class="kpi">
                      <div class="label">Type</div>
                      <div class="value" style="font-size: 18px;">{info.get('model_type', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with k3:
                roc_auc = metrics.get("roc_auc", 0)
                st.markdown(
                    f"""
                    <div class="kpi">
                      <div class="label">ROC-AUC</div>
                      <div class="value" style="font-size: 22px;">{roc_auc:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with k4:
                f1 = metrics.get("f1_score", 0)
                st.markdown(
                    f"""
                    <div class="kpi">
                      <div class="label">F1-score</div>
                      <div class="value" style="font-size: 22px;">{f1:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div class='rule'></div>", unsafe_allow_html=True)

            if metrics:
                fig = go.Figure()
                metric_names = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
                metric_values = [
                    metrics.get("accuracy", 0),
                    metrics.get("precision", 0),
                    metrics.get("recall", 0),
                    metrics.get("f1_score", 0),
                    metrics.get("roc_auc", 0),
                ]

                fig.add_trace(
                    go.Bar(
                        x=metric_names,
                        y=metric_values,
                        text=[f"{v:.3f}" for v in metric_values],
                        textposition="outside",
                    )
                )

                fig.update_layout(
                    title="Model performance",
                    title_font_size=18,
                    title_x=0.5,
                    yaxis=dict(range=[0, 1.1], title="Score"),
                    xaxis_title="Metric",
                    template="plotly_white",
                    height=380,
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    margin=dict(l=20, r=20, t=60, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Impossible de charger les informations du modèle: {str(e)}")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="paper">
          <h2 style="margin: 0.1rem 0 0.65rem 0;">Quick start</h2>
          <div style="color: rgba(15,23,42,0.70); font-size: 15px; line-height: 1.9;">
            <ol style="margin-top: 0.25rem;">
              <li><b>Single prediction</b>: analyze one customer in “Prediction”.</li>
              <li><b>Batch analysis</b>: upload a CSV to score multiple customers.</li>
              <li><b>Analytics</b>: explore distributions and summary indicators.</li>
            </ol>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# PAGE 2: SINGLE PREDICTION
# ============================================================================

elif page == "Prediction":
    st.markdown(
        """
        <div class="hero">
          <h1 style="margin: 0 0 0.35rem 0;">Single customer prediction</h1>
          <div style="color: rgba(15,23,42,0.68); font-size: 15.5px;">
            Enter customer attributes and get churn risk estimation
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='paper'>", unsafe_allow_html=True)

    with st.form("prediction_form"):
        st.markdown("### Customer profile")

        col1, col2, col3 = st.columns(3)

        with col1:
            customer_age = st.number_input("Age", min_value=18, max_value=100, value=45, help="Customer age")
            gender = st.selectbox("Gender", ["M", "F"])
            dependent_count = st.number_input("Dependents", min_value=0, max_value=10, value=3)

        with col2:
            education_level = st.selectbox(
                "Education level",
                ["High School", "Graduate", "Uneducated", "College", "Post-Graduate", "Doctorate"],
            )
            marital_status = st.selectbox("Marital status", ["Married", "Single", "Divorced"])
            income_category = st.selectbox(
                "Income category",
                ["Less than $40K", "$40K - $60K", "$60K - $80K", "$80K - $120K", "$120K +"],
            )

        with col3:
            card_category = st.selectbox("Card category", ["Blue", "Silver", "Gold", "Platinum"])
            months_on_book = st.number_input("Tenure (months)", min_value=0, value=39)
            total_relationship_count = st.number_input("Products count", min_value=1, max_value=6, value=5)

        st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
        st.markdown("### Banking activity")

        col4, col5, col6 = st.columns(3)

        with col4:
            months_inactive_12_mon = st.number_input("Inactive months (last 12 months)", min_value=0, max_value=12, value=1)
            contacts_count_12_mon = st.number_input("Contacts (last 12 months)", min_value=0, value=3)
            credit_limit = st.number_input("Credit limit ($)", min_value=0.0, value=12691.0, step=100.0)

        with col5:
            total_revolving_bal = st.number_input("Revolving balance ($)", min_value=0, value=777)
            avg_open_to_buy = st.number_input("Average available credit ($)", min_value=0.0, value=11914.0, step=100.0)
            total_amt_chng_q4_q1 = st.number_input("Amount change Q4/Q1", value=1.335, step=0.01)

        with col6:
            total_trans_amt = st.number_input("Total transaction amount ($)", min_value=0, value=1144)
            total_trans_ct = st.number_input("Total transaction count", min_value=0, value=42)
            total_ct_chng_q4_q1 = st.number_input("Transaction count change Q4/Q1", value=1.625, step=0.01)
            avg_utilization_ratio = st.number_input(
                "Average utilization ratio",
                min_value=0.0,
                max_value=1.0,
                value=0.061,
                step=0.001,
                format="%.3f",
            )

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("Run prediction")

        if submit:
            payload = {
                "customer_age": customer_age,
                "gender": gender,
                "dependent_count": dependent_count,
                "education_level": education_level,
                "marital_status": marital_status,
                "income_category": income_category,
                "card_category": card_category,
                "months_on_book": months_on_book,
                "total_relationship_count": total_relationship_count,
                "months_inactive_12_mon": months_inactive_12_mon,
                "contacts_count_12_mon": contacts_count_12_mon,
                "credit_limit": credit_limit,
                "total_revolving_bal": total_revolving_bal,
                "avg_open_to_buy": avg_open_to_buy,
                "total_amt_chng_q4_q1": total_amt_chng_q4_q1,
                "total_trans_amt": total_trans_amt,
                "total_trans_ct": total_trans_ct,
                "total_ct_chng_q4_q1": total_ct_chng_q4_q1,
                "avg_utilization_ratio": avg_utilization_ratio,
            }

            with st.spinner("Processing..."):
                try:
                    response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)

                    if response.status_code == 200:
                        result = response.json()
                        prediction = result["prediction"]
                        proba = result.get("probabilities", {})

                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

                        churn_proba = proba.get("churn", 0) if proba else (1 if prediction == 1 else 0)

                        if churn_proba >= 0.7:
                            risk_class = "risk-high"
                            risk_text = "HIGH RISK"
                        elif churn_proba >= 0.4:
                            risk_class = "risk-med"
                            risk_text = "MODERATE RISK"
                        else:
                            risk_class = "risk-low"
                            risk_text = "LOW RISK"

                        st.markdown(
                            f"""
                            <div class="prediction-banner">
                              <div class="title">Churn risk assessment</div>
                              <div class="risk {risk_class}">{risk_text}</div>
                              <div style="margin-top: 0.35rem; color: rgba(15,23,42,0.65); font-size: 13px;">
                                Probability estimate: <b>{churn_proba*100:.1f}%</b>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if proba:
                            fig = go.Figure(
                                go.Indicator(
                                    mode="gauge+number+delta",
                                    value=churn_proba * 100,
                                    domain={"x": [0, 1], "y": [0, 1]},
                                    title={"text": "Churn probability (%)", "font": {"size": 18}},
                                    delta={"reference": 50},
                                    gauge={
                                        "axis": {"range": [None, 100]},
                                        "bar": {"color": "#0f172a"},
                                        "bgcolor": "white",
                                        "borderwidth": 1,
                                        "bordercolor": "rgba(15,23,42,0.2)",
                                        "steps": [
                                            {"range": [0, 40], "color": "rgba(22,163,74,0.16)"},
                                            {"range": [40, 70], "color": "rgba(217,119,6,0.16)"},
                                            {"range": [70, 100], "color": "rgba(220,38,38,0.14)"},
                                        ],
                                        "threshold": {"line": {"color": "#dc2626", "width": 3}, "thickness": 0.75, "value": 70},
                                    },
                                )
                            )
                            fig.update_layout(
                                height=360,
                                paper_bgcolor="white",
                                font={"color": "#0f172a", "family": "Arial"},
                                margin=dict(l=20, r=20, t=50, b=10),
                            )
                            st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<div class='paper'>", unsafe_allow_html=True)
                        st.markdown("<h3 style='margin: 0.1rem 0 0.65rem 0;'>Recommendations</h3>", unsafe_allow_html=True)

                        if churn_proba >= 0.7:
                            st.error(
                                """
**Immediate actions**
- Proactive outreach via customer success
- Personalized retention offer
- Quick satisfaction check to identify friction points
- Offer migration to a better-fitting plan
"""
                            )
                        elif churn_proba >= 0.4:
                            st.warning(
                                """
**Preventive actions**
- Engagement campaign (email / in-app)
- Suggest relevant add-on services
- Monthly activity monitoring
- Optimize card benefits and limits
"""
                            )
                        else:
                            st.success(
                                """
**Relationship maintenance**
- Maintain service quality for a stable customer
- Identify upsell opportunities
- Referral program targeting
- Loyalty rewards alignment
"""
                            )

                        st.markdown("</div>", unsafe_allow_html=True)

                    else:
                        st.error(f"Erreur API: {response.text}")

                except Exception as e:
                    st.error(f"Erreur de connexion: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE 3: BATCH ANALYSIS
# ============================================================================

elif page == "Batch Analysis":
    st.markdown(
        """
        <div class="hero">
          <h1 style="margin: 0 0 0.35rem 0;">Batch analysis</h1>
          <div style="color: rgba(15,23,42,0.68); font-size: 15.5px;">
            Upload a CSV file to score multiple customers
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='paper'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin: 0.1rem 0 0.65rem 0;'>File upload</h3>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Select a CSV file",
        type="csv",
        help="The file must contain all required columns",
    )

    if uploaded_file is not None:
        st.success("File uploaded successfully.")

        df = pd.read_csv(uploaded_file)

        st.markdown(
            f"""
            <div style="display:flex; gap: 18px; flex-wrap: wrap; margin: 0.35rem 0 0.75rem 0;">
              <div style="color: rgba(15,23,42,0.65); font-size: 14px;"><b>Rows</b>: {len(df)}</div>
              <div style="color: rgba(15,23,42,0.65); font-size: 14px;"><b>Columns</b>: {len(df.columns)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("Data preview"):
            st.dataframe(df.head(10), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            process_btn = st.button("Run batch scoring", use_container_width=True)

        if process_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Sending file to API...")
            progress_bar.progress(25)

            try:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}

                status_text.text("Scoring in progress...")
                progress_bar.progress(50)

                response = requests.post(f"{API_URL}/predict-csv", files=files, timeout=60)

                if response.status_code == 200:
                    progress_bar.progress(75)
                    status_text.text("Processing results...")

                    from io import BytesIO
                    result_df = pd.read_csv(BytesIO(response.content))

                    progress_bar.progress(100)
                    status_text.text("Done.")

                    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                    st.markdown("<div class='paper'>", unsafe_allow_html=True)
                    st.markdown("<h2 style='margin: 0.1rem 0 0.9rem 0;'>Batch results</h2>", unsafe_allow_html=True)

                    n_churn = result_df["churn_prediction"].sum()
                    n_total = len(result_df)
                    churn_rate = (n_churn / n_total) * 100

                    k1, k2, k3, k4 = st.columns(4)
                    with k1:
                        st.markdown(
                            f"""
                            <div class="grid-card">
                              <div class="kpi">
                                <div class="label">Total customers</div>
                                <div class="value">{n_total}</div>
                                <div class="sub">Scored in this batch</div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with k2:
                        st.markdown(
                            f"""
                            <div class="grid-card">
                              <div class="kpi">
                                <div class="label">Churn risk</div>
                                <div class="value" style="color: var(--bad);">{n_churn}</div>
                                <div class="sub">Predicted churn</div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with k3:
                        st.markdown(
                            f"""
                            <div class="grid-card">
                              <div class="kpi">
                                <div class="label">Retained</div>
                                <div class="value" style="color: var(--ok);">{n_total - n_churn}</div>
                                <div class="sub">Predicted non-churn</div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with k4:
                        st.markdown(
                            f"""
                            <div class="grid-card">
                              <div class="kpi">
                                <div class="label">Churn rate</div>
                                <div class="value" style="color: var(--warn);">{churn_rate:.1f}%</div>
                                <div class="sub">Share of churn predictions</div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                    col_viz1, col_viz2 = st.columns(2)

                    with col_viz1:
                        st.markdown("<div class='paper'>", unsafe_allow_html=True)
                        fig_pie = px.pie(
                            values=[n_churn, n_total - n_churn],
                            names=["Churn", "Non-Churn"],
                            title="Churn distribution",
                            hole=0.45,
                        )
                        fig_pie.update_layout(
                            paper_bgcolor="white",
                            plot_bgcolor="white",
                            height=360,
                            margin=dict(l=20, r=20, t=60, b=20),
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with col_viz2:
                        if "proba_churn" in result_df.columns:
                            st.markdown("<div class='paper'>", unsafe_allow_html=True)
                            fig_hist = px.histogram(
                                result_df,
                                x="proba_churn",
                                nbins=30,
                                title="Churn probability distribution",
                            )
                            fig_hist.update_layout(
                                paper_bgcolor="white",
                                plot_bgcolor="white",
                                height=360,
                                xaxis_title="Churn probability",
                                yaxis_title="Customers",
                                margin=dict(l=20, r=20, t=60, b=20),
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        st.download_button(
                            label="Download results (CSV)",
                            data=response.content,
                            file_name=f"churn_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                    with st.expander("View full table"):
                        def highlight_churn(row):
                            if row["churn_prediction"] == 1:
                                return ["background-color: #fff1f2"] * len(row)
                            else:
                                return ["background-color: #f0fdf4"] * len(row)

                        styled_df = result_df.style.apply(highlight_churn, axis=1)
                        st.dataframe(styled_df, use_container_width=True, height=420)

                else:
                    st.error(f"Erreur API: {response.text}")

            except Exception as e:
                st.error(f"Erreur: {str(e)}")

    else:
        st.info("No file selected yet. Upload a CSV to start batch scoring.")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE 4: ANALYTICS
# ============================================================================

elif page == "Analytics":
    st.markdown(
        """
        <div class="hero">
          <h1 style="margin: 0 0 0.35rem 0;">Analytics</h1>
          <div style="color: rgba(15,23,42,0.68); font-size: 15.5px;">
            Advanced views and business-ready indicators
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("<div class='paper'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin: 0.1rem 0 0.65rem 0;'>Key indicators</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Total predictions</div>
                <div class="value">1,247</div>
                <div class="sub">Rolling 30 days</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Average churn rate</div>
                <div class="value" style="color: var(--bad);">16.2%</div>
                <div class="sub">Change vs previous month</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Model accuracy</div>
                <div class="value" style="color: var(--ok);">94.3%</div>
                <div class="sub">Latest evaluation</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="grid-card">
              <div class="kpi">
                <div class="label">Saved customers</div>
                <div class="value" style="color: var(--warn);">89</div>
                <div class="sub">Preventive actions</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("<div class='paper'>", unsafe_allow_html=True)
        dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
        churn_rate = [15 + i * 0.1 + (i % 5) for i in range(30)]

        fig_trend = px.line(
            x=dates,
            y=churn_rate,
            title="Churn rate trend",
            labels={"x": "Date", "y": "Churn rate (%)"},
        )
        fig_trend.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=360,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='paper'>", unsafe_allow_html=True)
        categories = ["Blue", "Silver", "Gold", "Platinum"]
        churn_by_card = [18, 15, 12, 8]

        fig_bar = px.bar(
            x=categories,
            y=churn_by_card,
            title="Churn rate by card category",
            labels={"x": "Card category", "y": "Churn rate (%)"},
        )
        fig_bar.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=360,
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="paper">
          <h3 style="margin: 0.1rem 0 0.65rem 0;">Actionable insights</h3>
          <div style="color: rgba(15,23,42,0.70); font-size: 15px; line-height: 1.9;">
            <ul style="margin-top: 0.25rem;">
              <li><b>Alert:</b> churn rate increased by 2.1% this month (simulated).</li>
              <li><b>Highest risk segment:</b> Blue card customers (simulated).</li>
              <li><b>Operational:</b> 89 at-risk customers were successfully contacted (simulated).</li>
              <li><b>Model:</b> accuracy at 94.3% on the latest evaluation (simulated).</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
