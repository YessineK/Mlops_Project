# frontend/app.py
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
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - DESIGN MODERNE
# ============================================================================

st.markdown("""
<style>
    /* Theme principal */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Prediction Cards */
    .prediction-card {
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .churn-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        border: 3px solid #c92a2a;
    }
    
    .churn-medium {
        background: linear-gradient(135deg, #ffd93d 0%, #ffb700 100%);
        color: #2d2d2d;
        border: 3px solid #f59f00;
    }
    
    .churn-low {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
        border: 3px solid #2b8a3e;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3561 0%, #1e2749 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Input fields */
    .stNumberInput>div>div>input,
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border 0.3s ease;
    }
    
    .stNumberInput>div>div>input:focus,
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border: 2px solid #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Headers */
    h1 {
        color: white !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    h2, h3 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Logo
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 60px;'>🏦</div>
            <h2 style='margin: 0; color: white;'>Churn AI</h2>
            <p style='color: #a0aec0; font-size: 14px;'>Powered by MLOps</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "📍 Navigation",
        ["🏠 Dashboard", "🔍 Prediction", "📊 Batch Analysis", "📈 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 🔌 System Status")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            
            if status == "healthy":
                st.success("✅ API Online")
                st.info(f"🤖 Model Loaded")
            else:
                st.warning(f"⚠️ Status: {status}")
        else:
            st.error("❌ API Error")
    except Exception as e:
        st.error("❌ API Offline")
        st.caption(f"Error: {str(e)[:50]}")
    
    st.markdown("---")
    
    # Info
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: #a0aec0; font-size: 12px;'>
            MLOps Project 2025<br>
            Churn Prediction System<br>
            v2.0.0
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================

if page == "🏠 Dashboard":
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>🏦 Bank Churn Prediction</h1>
        <p style='font-size: 1.2rem; color: rgba(255,255,255,0.8);'>
            Prédisez et prévenez le départ de vos clients avec l'IA
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 48px; margin-bottom: 10px;'>🎯</div>
            <h3 style='color: #667eea; margin: 10px 0;'>Précision</h3>
            <p style='color: #666; font-size: 14px;'>
                Modèles ML de pointe<br>
                avec >90% de précision
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 48px; margin-bottom: 10px;'>⚡</div>
            <h3 style='color: #764ba2; margin: 10px 0;'>Temps Réel</h3>
            <p style='color: #666; font-size: 14px;'>
                Prédictions instantanées<br>
                en quelques millisecondes
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style='font-size: 48px; margin-bottom: 10px;'>📊</div>
            <h3 style='color: #667eea; margin: 10px 0;'>Analytics</h3>
            <p style='color: #666; font-size: 14px;'>
                Insights actionnables<br>
                et visualisations avancées
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Model Info
    try:
        response = requests.get(f"{API_URL}/model-info", timeout=3)
        if response.status_code == 200:
            info = response.json()
            
            st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                <h2 style='color: #2d3561; text-align: center; margin-bottom: 2rem;'>📊 Informations du Modèle</h2>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <p style='color: #999; font-size: 14px; margin: 0;'>Modèle</p>
                    <h3 style='color: #667eea; margin: 5px 0;'>{info.get('model_name', 'N/A').split('(')[0]}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <p style='color: #999; font-size: 14px; margin: 0;'>Type</p>
                    <h3 style='color: #764ba2; margin: 5px 0;'>{info.get('model_type', 'N/A')}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                metrics = info.get('metrics', {})
                roc_auc = metrics.get('roc_auc', 0)
                st.markdown(f"""
                <div style='text-align: center;'>
                    <p style='color: #999; font-size: 14px; margin: 0;'>ROC-AUC</p>
                    <h3 style='color: #51cf66; margin: 5px 0;'>{roc_auc:.3f}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                f1 = metrics.get('f1_score', 0)
                st.markdown(f"""
                <div style='text-align: center;'>
                    <p style='color: #999; font-size: 14px; margin: 0;'>F1-Score</p>
                    <h3 style='color: #ff6b6b; margin: 5px 0;'>{f1:.3f}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Metrics Chart
            if metrics:
                st.markdown("<br>", unsafe_allow_html=True)
                
                fig = go.Figure()
                
                metric_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
                metric_values = [
                    metrics.get('accuracy', 0),
                    metrics.get('precision', 0),
                    metrics.get('recall', 0),
                    metrics.get('f1_score', 0),
                    metrics.get('roc_auc', 0)
                ]
                
                fig.add_trace(go.Bar(
                    x=metric_names,
                    y=metric_values,
                    marker=dict(
                        color=metric_values,
                        colorscale='Viridis',
                        line=dict(color='rgb(8,48,107)', width=2)
                    ),
                    text=[f'{v:.3f}' for v in metric_values],
                    textposition='outside',
                ))
                
                fig.update_layout(
                    title='Performance du Modèle',
                    title_font_size=20,
                    title_x=0.5,
                    yaxis=dict(range=[0, 1.1], title='Score'),
                    xaxis_title='Métriques',
                    template='plotly_white',
                    height=400,
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.warning(f"⚠️ Impossible de charger les informations du modèle: {str(e)}")
    
    # Quick Start
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        <h2 style='color: #2d3561; margin-bottom: 1rem;'>🚀 Guide de Démarrage Rapide</h2>
        <ol style='color: #666; font-size: 16px; line-height: 2;'>
            <li><strong>Prédiction Unique:</strong> Analysez un client individuel dans l'onglet "Prediction"</li>
            <li><strong>Analyse en Batch:</strong> Uploadez un fichier CSV pour analyser plusieurs clients</li>
            <li><strong>Analytics:</strong> Visualisez les tendances et insights de vos prédictions</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE 2: SINGLE PREDICTION
# ============================================================================

elif page == "🔍 Prediction":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem;'>🔍 Analyse Client Individuel</h1>
        <p style='font-size: 1.1rem; color: rgba(255,255,255,0.8);'>
            Prédisez le risque de churn pour un client spécifique
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Form Container
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
    """, unsafe_allow_html=True)
    
    with st.form("prediction_form"):
        st.markdown("### 👤 Informations Client")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            customer_age = st.number_input(
                "Âge", 
                min_value=18, 
                max_value=100, 
                value=45,
                help="Âge du client"
            )
            gender = st.selectbox("Genre", ["M", "F"])
            dependent_count = st.number_input(
                "Personnes à charge", 
                min_value=0, 
                max_value=10, 
                value=3
            )
        
        with col2:
            education_level = st.selectbox(
                "Niveau d'éducation",
                ["High School", "Graduate", "Uneducated", "College", 
                 "Post-Graduate", "Doctorate"]
            )
            marital_status = st.selectbox(
                "Statut marital",
                ["Married", "Single", "Divorced"]
            )
            income_category = st.selectbox(
                "Catégorie de revenu",
                ["Less than $40K", "$40K - $60K", "$60K - $80K", 
                 "$80K - $120K", "$120K +"]
            )
        
        with col3:
            card_category = st.selectbox(
                "Type de carte",
                ["Blue", "Silver", "Gold", "Platinum"]
            )
            months_on_book = st.number_input(
                "Ancienneté (mois)", 
                min_value=0, 
                value=39
            )
            total_relationship_count = st.number_input(
                "Nombre de produits", 
                min_value=1, 
                max_value=6, 
                value=5
            )
        
        st.markdown("---")
        st.markdown("### 💳 Activité Bancaire")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            months_inactive_12_mon = st.number_input(
                "Mois d'inactivité (12 derniers mois)", 
                min_value=0, 
                max_value=12, 
                value=1
            )
            contacts_count_12_mon = st.number_input(
                "Contacts (12 derniers mois)", 
                min_value=0, 
                value=3
            )
            credit_limit = st.number_input(
                "Limite de crédit ($)", 
                min_value=0.0, 
                value=12691.0,
                step=100.0
            )
        
        with col5:
            total_revolving_bal = st.number_input(
                "Solde revolving ($)", 
                min_value=0, 
                value=777
            )
            avg_open_to_buy = st.number_input(
                "Crédit disponible moyen ($)", 
                min_value=0.0, 
                value=11914.0,
                step=100.0
            )
            total_amt_chng_q4_q1 = st.number_input(
                "Changement montant Q4/Q1", 
                value=1.335,
                step=0.01
            )
        
        with col6:
            total_trans_amt = st.number_input(
                "Montant total transactions ($)", 
                min_value=0, 
                value=1144
            )
            total_trans_ct = st.number_input(
                "Nombre total transactions", 
                min_value=0, 
                value=42
            )
            total_ct_chng_q4_q1 = st.number_input(
                "Changement nb transactions Q4/Q1", 
                value=1.625,
                step=0.01
            )
            avg_utilization_ratio = st.number_input(
                "Taux d'utilisation moyen", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.061,
                step=0.001,
                format="%.3f"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("🔮 Prédire le Risque de Churn")
        
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
                "avg_utilization_ratio": avg_utilization_ratio
            }
            
            with st.spinner("🔄 Analyse en cours..."):
                try:
                    response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        prediction = result["prediction"]
                        proba = result.get("probabilities", {})
                        
                        # Display Results
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Probability gauge
                        churn_proba = proba.get("churn", 0) if proba else (1 if prediction == 1 else 0)
                        
                        # Determine risk level
                        if churn_proba >= 0.7:
                            risk_class = "churn-high"
                            risk_text = "🚨 RISQUE ÉLEVÉ"
                            risk_emoji = "🔴"
                        elif churn_proba >= 0.4:
                            risk_class = "churn-medium"
                            risk_text = "⚠️ RISQUE MODÉRÉ"
                            risk_emoji = "🟡"
                        else:
                            risk_class = "churn-low"
                            risk_text = "✅ RISQUE FAIBLE"
                            risk_emoji = "🟢"
                        
                        st.markdown(f"""
                        <div class="prediction-card {risk_class}">
                            {risk_emoji} {risk_text}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Gauge Chart
                        if proba:
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=churn_proba * 100,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': "Probabilité de Churn (%)", 'font': {'size': 24}},
                                delta={'reference': 50, 'increasing': {'color': "red"}},
                                gauge={
                                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                    'bar': {'color': "darkblue"},
                                    'bgcolor': "white",
                                    'borderwidth': 2,
                                    'bordercolor': "gray",
                                    'steps': [
                                        {'range': [0, 40], 'color': '#51cf66'},
                                        {'range': [40, 70], 'color': '#ffd93d'},
                                        {'range': [70, 100], 'color': '#ff6b6b'}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 70
                                    }
                                }
                            ))
                            
                            fig.update_layout(
                                height=400,
                                paper_bgcolor="white",
                                font={'color': "darkblue", 'family': "Arial"}
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommendations
                        st.markdown("""
                        <div style='background: white; padding: 2rem; border-radius: 15px; margin-top: 2rem;'>
                            <h3 style='color: #2d3561;'>💡 Recommandations</h3>
                        """, unsafe_allow_html=True)
                        
                        if churn_proba >= 0.7:
                            st.error("""
                            **Actions Urgentes:**
                            - 📞 Contact immédiat du client par le service relation client
                            - 🎁 Offre promotionnelle personnalisée
                            - 💬 Enquête de satisfaction pour identifier les points de friction
                            - 🔄 Proposition de migration vers une offre plus adaptée
                            """)
                        elif churn_proba >= 0.4:
                            st.warning("""
                            **Actions Préventives:**
                            - 📧 Campagne d'engagement par email
                            - 🎯 Proposition de services complémentaires
                            - 📊 Suivi mensuel de l'activité
                            - 💳 Optimisation des avantages carte
                            """)
                        else:
                            st.success("""
                            **Maintien de la Relation:**
                            - ⭐ Client fidèle - maintenir la qualité de service
                            - 📈 Opportunité d'up-selling
                            - 💌 Programme de parrainage
                            - 🎊 Récompenses de fidélité
                            """)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    else:
                        st.error(f"❌ Erreur API: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Erreur de connexion: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE 3: BATCH ANALYSIS
# ============================================================================

elif page == "📊 Batch Analysis":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem;'>📊 Analyse en Batch</h1>
        <p style='font-size: 1.1rem; color: rgba(255,255,255,0.8);'>
            Analysez plusieurs clients simultanément via fichier CSV
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        <h3 style='color: #2d3561; margin-bottom: 1rem;'>📁 Upload de Fichier</h3>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier CSV",
        type="csv",
        help="Le fichier doit contenir toutes les colonnes nécessaires"
    )
    
    if uploaded_file is not None:
        st.success("✅ Fichier uploadé avec succès!")
        
        # Preview
        df = pd.read_csv(uploaded_file)
        
        st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <p style='color: #666;'><strong>Nombre de lignes:</strong> {len(df)}</p>
            <p style='color: #666;'><strong>Nombre de colonnes:</strong> {len(df.columns)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("👁️ Aperçu des données"):
            st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Process Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            process_btn = st.button("🚀 Lancer l'Analyse", use_container_width=True)
        
        if process_btn:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Envoi du fichier à l'API...")
            progress_bar.progress(25)
            
            try:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                
                status_text.text("🤖 Analyse en cours...")
                progress_bar.progress(50)
                
                response = requests.post(f"{API_URL}/predict-csv", files=files, timeout=60)
                
                if response.status_code == 200:
                    progress_bar.progress(75)
                    status_text.text("✅ Traitement des résultats...")
                    
                    # Read results
                    from io import BytesIO
                    result_df = pd.read_csv(BytesIO(response.content))
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analyse terminée!")
                    
                    st.balloons()
                    
                    # Results Summary
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                        <h2 style='color: #2d3561; text-align: center;'>📊 Résultats de l'Analyse</h2>
                    """, unsafe_allow_html=True)
                    
                    # Stats
                    n_churn = result_df['churn_prediction'].sum()
                    n_total = len(result_df)
                    churn_rate = (n_churn / n_total) * 100
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <p style='color: #999; font-size: 14px;'>Total Clients</p>
                            <h2 style='color: #667eea; margin: 10px 0;'>{n_total}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <p style='color: #999; font-size: 14px;'>Risque de Churn</p>
                            <h2 style='color: #ff6b6b; margin: 10px 0;'>{n_churn}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <p style='color: #999; font-size: 14px;'>Clients Fidèles</p>
                            <h2 style='color: #51cf66; margin: 10px 0;'>{n_total - n_churn}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <p style='color: #999; font-size: 14px;'>Taux de Churn</p>
                            <h2 style='color: #ffd93d; margin: 10px 0;'>{churn_rate:.1f}%</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Visualization
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_viz1, col_viz2 = st.columns(2)
                    
                    with col_viz1:
                        # Pie Chart
                        fig_pie = px.pie(
                            values=[n_churn, n_total - n_churn],
                            names=['Churn', 'Non-Churn'],
                            title='Distribution Churn vs Non-Churn',
                            color_discrete_sequence=['#ff6b6b', '#51cf66'],
                            hole=0.4
                        )
                        fig_pie.update_layout(
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            height=400
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col_viz2:
                        # Probability Distribution
                        if 'proba_churn' in result_df.columns:
                            fig_hist = px.histogram(
                                result_df,
                                x='proba_churn',
                                nbins=30,
                                title='Distribution des Probabilités de Churn',
                                color_discrete_sequence=['#667eea']
                            )
                            fig_hist.update_layout(
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                height=400,
                                xaxis_title='Probabilité de Churn',
                                yaxis_title='Nombre de Clients'
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # Download Button
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        st.download_button(
                            label="📥 Télécharger les Résultats (CSV)",
                            data=response.content,
                            file_name=f"churn_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    # Preview Results Table
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    with st.expander("📋 Voir le Tableau Complet"):
                        # Color coding
                        def highlight_churn(row):
                            if row['churn_prediction'] == 1:
                                return ['background-color: #ffebee'] * len(row)
                            else:
                                return ['background-color: #e8f5e9'] * len(row)
                        
                        styled_df = result_df.style.apply(highlight_churn, axis=1)
                        st.dataframe(styled_df, use_container_width=True, height=400)
                
                else:
                    st.error(f"❌ Erreur API: {response.text}")
            
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #666;'>
            <div style='font-size: 80px; margin-bottom: 1rem;'>📂</div>
            <h3>Aucun fichier uploadé</h3>
            <p>Uploadez un fichier CSV pour commencer l'analyse</p>
        </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE 4: ANALYTICS
# ============================================================================

elif page == "📈 Analytics":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='font-size: 2.5rem;'>📈 Analytics & Insights</h1>
        <p style='font-size: 1.1rem; color: rgba(255,255,255,0.8);'>
            Visualisations avancées et métriques business
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample data for demo
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        <h3 style='color: #2d3561;'>🎯 Métriques Clés</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p style='color: #999; font-size: 14px;'>Prédictions Totales</p>
            <h2 style='color: #667eea;'>1,247</h2>
            <p style='color: #51cf66; font-size: 12px;'>↑ 12% ce mois</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p style='color: #999; font-size: 14px;'>Taux de Churn Moyen</p>
            <h2 style='color: #ff6b6b;'>16.2%</h2>
            <p style='color: #ff6b6b; font-size: 12px;'>↑ 2.1% vs mois dernier</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <p style='color: #999; font-size: 14px;'>Précision Modèle</p>
            <h2 style='color: #51cf66;'>94.3%</h2>
            <p style='color: #51cf66; font-size: 12px;'>↑ 0.5% amélioration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p style='color: #999; font-size: 14px;'>Clients Sauvés</p>
            <h2 style='color: #ffd93d;'>89</h2>
            <p style='color: #51cf66; font-size: 12px;'>Actions préventives</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div><br>", unsafe_allow_html=True)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        # Sample trend data
        dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
        churn_rate = [15 + i * 0.1 + (i % 5) for i in range(30)]
        
        fig_trend = px.line(
            x=dates,
            y=churn_rate,
            title='Évolution du Taux de Churn',
            labels={'x': 'Date', 'y': 'Taux de Churn (%)'}
        )
        fig_trend.update_traces(line_color='#667eea', line_width=3)
        fig_trend.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=350
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_chart2:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        # Sample category data
        categories = ['Blue', 'Silver', 'Gold', 'Platinum']
        churn_by_card = [18, 15, 12, 8]
        
        fig_bar = px.bar(
            x=categories,
            y=churn_by_card,
            title='Taux de Churn par Type de Carte',
            labels={'x': 'Type de Carte', 'y': 'Taux de Churn (%)'},
            color=churn_by_card,
            color_continuous_scale='RdYlGn_r'
        )
        fig_bar.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin-top: 2rem;'>
        <h3 style='color: #2d3561;'>💡 Insights Actionnables</h3>
        <ul style='color: #666; font-size: 16px; line-height: 2;'>
            <li>🔴 <strong>Alerte:</strong> Augmentation de 2.1% du taux de churn ce mois</li>
            <li>📊 Les clients avec carte <strong>Blue</strong> ont le taux de churn le plus élevé (18%)</li>
            <li>✅ 89 clients identifiés à risque ont été contactés avec succès</li>
            <li>📈 Le modèle s'améliore avec une précision de 94.3%</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)