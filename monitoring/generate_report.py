#!/usr/bin/env python3
"""
Script de monitoring combiné : Data Drift + Performance
Compatible avec Evidently (versions récentes)
"""

import os
import json
from datetime import datetime

import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

# =========================
# CONFIG
# =========================
PRED = "prediction"
PROBA = "proba"
TARGET_CANDIDATES = ["churn", "Attrition_Flag"]


# =========================
# HELPER FUNCTIONS
# =========================
def find_target_column(df: pd.DataFrame):
    """Trouve la colonne target dans le DataFrame"""
    for col in TARGET_CANDIDATES:
        if col in df.columns:
            return col
    return None


def compute_metrics(df: pd.DataFrame, target_col: str):
    """Calcule les métriques de performance"""
    y_true = df[target_col].astype(int)
    y_pred = df[PRED].astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

    # AUC seulement si proba disponible
    if PROBA in df.columns and df[PROBA].notna().any():
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, df[PROBA].astype(float)))
        except Exception:
            metrics["roc_auc"] = None
    else:
        metrics["roc_auc"] = None

    return metrics


def fmt(x, nd=3):
    """Formate un nombre pour l'affichage"""
    if x is None:
        return "—"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def delta_class(d):
    """Retourne la classe CSS selon le delta"""
    if d is None:
        return "neutral"
    return "bad" if d < 0 else "good"


def build_performance_html(data: dict) -> str:
    """Génère le rapport HTML de performance"""
    ref = data["reference"]
    cur = data["current"]
    delta = data["delta"]
    alerts = data.get("alerts", [])

    cm = cur.get("confusion_matrix", [[0, 0], [0, 0]])
    tn, fp = cm[0]
    fn, tp = cm[1]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def metric_card(name, key):
        return f"""
        <div class="card">
          <div class="kpi-title">{name}</div>
          <div class="kpi-row">
            <div class="kpi-val">{fmt(cur.get(key))}</div>
            <div class="kpi-delta {delta_class(delta.get(key))}">
              {("+" if (delta.get(key) is not None and delta.get(key) > 0) else "")}{fmt(delta.get(key))}
            </div>
          </div>
          <div class="kpi-sub">ref: {fmt(ref.get(key))}</div>
        </div>
        """

    alerts_html = "".join([f"<li>{a}</li>" for a in alerts]) if alerts else "<li>No alerts ✅</li>"

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Model Performance Monitoring</title>
  <style>
    :root {{
      --bg: #0b0f17;
      --card: #121a27;
      --text: #e8eefc;
      --muted: #9fb0d0;
      --good: #1db954;
      --bad: #ff4d4d;
      --neutral: #7f8ea8;
      --border: rgba(255,255,255,0.08);
    }}
    body {{
      margin: 0; font-family: Inter, Arial, sans-serif;
      background: var(--bg); color: var(--text);
    }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px; }}
    h1 {{ margin: 0 0 6px 0; font-size: 32px; }}
    .sub {{ color: var(--muted); margin-bottom: 18px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 14px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    }}
    .kpi-title {{ color: var(--muted); font-size: 13px; margin-bottom: 6px; }}
    .kpi-row {{ display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }}
    .kpi-val {{ font-size: 26px; font-weight: 700; }}
    .kpi-delta {{
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      font-size: 13px;
    }}
    .kpi-delta.good {{ color: var(--good); }}
    .kpi-delta.bad {{ color: var(--bad); }}
    .kpi-delta.neutral {{ color: var(--neutral); }}
    .kpi-sub {{ margin-top: 6px; color: var(--muted); font-size: 12px; }}
    .section {{ margin-top: 18px; }}
    .section h2 {{ font-size: 18px; margin: 0 0 10px 0; }}
    .two {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 14px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--border);
      padding: 10px 8px;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
      color: var(--muted);
      font-size: 12px;
    }}
    .alerts {{
      background: rgba(255, 208, 0, 0.08);
      border: 1px solid rgba(255, 208, 0, 0.22);
    }}
    .alerts ul {{ margin: 10px 0 0 18px; }}
    .cm {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 10px;
    }}
    .cm .cell {{
      border-radius: 14px;
      border: 1px solid var(--border);
      padding: 12px;
      background: rgba(255,255,255,0.03);
    }}
    .cell .label {{ color: var(--muted); font-size: 12px; }}
    .cell .value {{ font-size: 22px; font-weight: 800; margin-top: 4px; }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: repeat(2, 1fr); }}
      .two {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Model Performance Monitoring</h1>
    <div class="sub">Generated: {now} • Current vs Reference</div>

    <div class="grid">
      {metric_card("Accuracy", "accuracy")}
      {metric_card("Precision", "precision")}
      {metric_card("Recall", "recall")}
      {metric_card("F1-score", "f1")}
      {metric_card("ROC AUC", "roc_auc")}
    </div>

    <div class="section two">
      <div class="card">
        <h2>Metrics Table <span class="pill">current / ref / delta</span></h2>
        <table>
          <thead>
            <tr><th>Metric</th><th>Reference</th><th>Current</th><th>Delta</th></tr>
          </thead>
          <tbody>
            <tr><td>Accuracy</td><td>{fmt(ref.get("accuracy"))}</td><td>{fmt(cur.get("accuracy"))}</td><td class="{delta_class(delta.get("accuracy"))}">{fmt(delta.get("accuracy"))}</td></tr>
            <tr><td>Precision</td><td>{fmt(ref.get("precision"))}</td><td>{fmt(cur.get("precision"))}</td><td class="{delta_class(delta.get("precision"))}">{fmt(delta.get("precision"))}</td></tr>
            <tr><td>Recall</td><td>{fmt(ref.get("recall"))}</td><td>{fmt(cur.get("recall"))}</td><td class="{delta_class(delta.get("recall"))}">{fmt(delta.get("recall"))}</td></tr>
            <tr><td>F1-score</td><td>{fmt(ref.get("f1"))}</td><td>{fmt(cur.get("f1"))}</td><td class="{delta_class(delta.get("f1"))}">{fmt(delta.get("f1"))}</td></tr>
            <tr><td>ROC AUC</td><td>{fmt(ref.get("roc_auc"))}</td><td>{fmt(cur.get("roc_auc"))}</td><td class="{delta_class(delta.get("roc_auc"))}">{fmt(delta.get("roc_auc"))}</td></tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>Confusion Matrix (Current)</h2>
        <div class="cm">
          <div class="cell"><div class="label">TN</div><div class="value">{tn}</div></div>
          <div class="cell"><div class="label">FP</div><div class="value">{fp}</div></div>
          <div class="cell"><div class="label">FN</div><div class="value">{fn}</div></div>
          <div class="cell"><div class="label">TP</div><div class="value">{tp}</div></div>
        </div>

        <div class="section alerts card" style="margin-top:14px;">
          <h2>Alerts</h2>
          <ul>{alerts_html}</ul>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""
    return html


# =========================
# DRIFT PART
# =========================
def run_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame, base_dir: str):
    """
    Génère le rapport de drift avec Evidently
    Essaie différents imports pour compatibilité
    """
    
    print("📊 Génération du rapport Data Drift...")
    
    # Nettoyage des colonnes inutiles
    for df in (reference_data, current_data):
        df.drop(columns=["CLIENTNUM", "Unnamed: 21"], errors="ignore", inplace=True)
    
    try:
        # ===== TENTATIVE 1: API moderne (Evidently >= 0.4.0) =====
        try:
            from evidently.report import Report
            from evidently.metric_preset import DataDriftPreset, DataQualityPreset
            
            print("✅ Utilisation de l'API Evidently moderne (Report)")
            
            report = Report(metrics=[
                DataDriftPreset(),
                DataQualityPreset()
            ])
            
            report.run(
                reference_data=reference_data,
                current_data=current_data
            )
            
            report_path = os.path.join(base_dir, "monitoring_report.html")
            report.save_html(report_path)
            print(f"✅ Rapport HTML sauvegardé: {report_path}")
            
            json_path = os.path.join(base_dir, "monitoring_tests.json")
            report.save_json(json_path)
            print(f"✅ Rapport JSON sauvegardé: {json_path}")
            
            # Analyser les résultats
            report_dict = report.as_dict()
            analyze_drift_results(report_dict)
            
            return True
            
        except (ImportError, AttributeError) as e:
            print(f"⚠️ API moderne non disponible: {e}")
            print("🔄 Tentative avec l'ancienne API...")
        
        # ===== TENTATIVE 2: API legacy (Evidently < 0.4.0) =====
        try:
            from evidently.dashboard import Dashboard
            from evidently.tabs import DataDriftTab
            
            print("✅ Utilisation de l'API Evidently legacy (Dashboard)")
            
            dashboard = Dashboard(tabs=[DataDriftTab()])
            dashboard.calculate(reference_data, current_data)
            
            report_path = os.path.join(base_dir, "monitoring_report.html")
            dashboard.save(report_path)
            print(f"✅ Rapport HTML sauvegardé: {report_path}")
            
            # Créer un JSON minimal
            json_path = os.path.join(base_dir, "monitoring_tests.json")
            with open(json_path, "w") as f:
                json.dump({
                    "summary": {"status": "completed", "api": "legacy"},
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            print(f"✅ Rapport JSON sauvegardé: {json_path}")
            
            return True
            
        except (ImportError, AttributeError) as e2:
            print(f"⚠️ API legacy non disponible: {e2}")
            raise Exception("Aucune API Evidently compatible trouvée")
    
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport de drift: {e}")
        import traceback
        traceback.print_exc()
        return False


def analyze_drift_results(report_dict: dict):
    """Analyse les résultats de drift"""
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DU DRIFT")
    print("="*80)
    
    drift_count = 0
    total_features = 0
    
    for metric in report_dict.get('metrics', []):
        if 'result' in metric:
            result = metric['result']
            if 'drift_by_columns' in result:
                drift_by_columns = result['drift_by_columns']
                for col, drift_info in drift_by_columns.items():
                    total_features += 1
                    if drift_info.get('drift_detected', False):
                        drift_count += 1
                        print(f"⚠️  Drift détecté sur: {col}")
    
    if total_features > 0:
        drift_pct = (drift_count/total_features*100)
        print(f"\nTotal features analysées: {total_features}")
        print(f"Features avec drift détecté: {drift_count}")
        print(f"Pourcentage de drift: {drift_pct:.1f}%")
        
        if drift_pct > 50:
            print("\n🔴 ALERTE: Drift élevé détecté!")
            print("   → Réentraîner le modèle avec les nouvelles données")
        elif drift_pct > 25:
            print("\n🟡 ATTENTION: Drift modéré détecté")
            print("   → Surveiller l'évolution")
        else:
            print("\n🟢 OK: Drift faible, modèle stable")
    else:
        print("✅ Aucun drift détecté")
    
    print("="*80)


# =========================
# MAIN
# =========================
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    # CORRECTION: Utiliser les bons noms de fichiers (sans _scored)
    ref_path = os.path.join(data_dir, "reference_data.csv")
    cur_path = os.path.join(data_dir, "current_data.csv")

    print("="*80)
    print("📊 MONITORING DATA DRIFT + PERFORMANCE")
    print("="*80)

    # Vérifier les fichiers
    if not os.path.exists(ref_path) or not os.path.exists(cur_path):
        print("❌ Erreur: Fichiers de données introuvables.")
        print(f"   Reference: {ref_path}")
        print(f"   Current: {cur_path}")
        print("\n💡 Exécutez d'abord: python prepare_data.py && python score_data.py")
        return

    print(f"✅ Fichiers trouvés:")
    print(f"   Reference: {ref_path}")
    print(f"   Current: {cur_path}")

    # Charger les données
    print("\n📥 Chargement des données...")
    reference_data = pd.read_csv(ref_path)
    current_data = pd.read_csv(cur_path)

    print(f"   Reference shape: {reference_data.shape}")
    print(f"   Current shape: {current_data.shape}")
    
    # Vérifier si les colonnes de prédiction existent
    has_predictions = PRED in reference_data.columns and PRED in current_data.columns
    
    if not has_predictions:
        print("\n⚠️ Colonnes de prédiction manquantes!")
        print("   Exécution de score_data.py en cours...")
        
        # Essayer d'exécuter score_data.py automatiquement
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, "score_data.py"], 
                                  capture_output=True, text=True, cwd=base_dir)
            if result.returncode == 0:
                print("✅ Scoring terminé avec succès!")
                # Recharger les données
                reference_data = pd.read_csv(ref_path)
                current_data = pd.read_csv(cur_path)
            else:
                print("❌ Erreur lors du scoring:")
                print(result.stderr)
                print("\n💡 Exécutez manuellement: python score_data.py")
                return
        except Exception as e:
            print(f"❌ Impossible d'exécuter score_data.py: {e}")
            print("\n💡 Exécutez manuellement: python score_data.py")
            return

    # ===== 1) DRIFT =====
    print("\n" + "="*80)
    print("🔍 PARTIE 1: ANALYSE DU DRIFT")
    print("="*80)
    
    drift_success = run_drift(reference_data.copy(), current_data.copy(), base_dir)

    # ===== 2) PERFORMANCE =====
    print("\n" + "="*80)
    print("🎯 PARTIE 2: MONITORING PERFORMANCE")
    print("="*80)

    # Vérifier les colonnes nécessaires
    if PRED not in reference_data.columns or PRED not in current_data.columns:
        print("❌ Colonne 'prediction' toujours manquante après le scoring.")
        print("   Le monitoring de performance est ignoré.")
        return

    target_ref = find_target_column(reference_data)
    target_cur = find_target_column(current_data)

    if target_ref is None or target_cur is None:
        print(f"❌ Colonne cible manquante. Besoin de: {TARGET_CANDIDATES}")
        return

    target_col = target_ref

    print("✅ Calcul des métriques de performance...")
    ref_metrics = compute_metrics(reference_data, target_col)
    cur_metrics = compute_metrics(current_data, target_col)

    result = {
        "reference": ref_metrics,
        "current": cur_metrics,
        "delta": {
            k: (None if (ref_metrics.get(k) is None or cur_metrics.get(k) is None)
                else float(cur_metrics[k] - ref_metrics[k]))
            for k in ["accuracy", "precision", "recall", "f1", "roc_auc"]
        }
    }

    # Alertes
    alerts = []
    if result["current"]["accuracy"] < 0.75:
        alerts.append("ALERT: accuracy < 0.75")
    if result["current"]["f1"] < 0.60:
        alerts.append("ALERT: f1 < 0.60")
    if result["delta"]["accuracy"] is not None and result["delta"]["accuracy"] < -0.05:
        alerts.append("ALERT: accuracy dropped by more than 0.05")
    result["alerts"] = alerts

    # Sauvegarder JSON
    metrics_json_path = os.path.join(base_dir, "performance_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Métriques sauvegardées: {metrics_json_path}")

    # Sauvegarder HTML
    html_path = os.path.join(base_dir, "performance_report.html")
    html = build_performance_html(result)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Rapport HTML sauvegardé: {html_path}")

    # Afficher les alertes
    if alerts:
        print("\n⚠️ Alertes de performance:")
        for a in alerts:
            print(f"   - {a}")
    else:
        print("\n✅ Aucune alerte de performance.")

    print("\n" + "="*80)
    print("✅ MONITORING TERMINÉe (drift + performance)")
    print("="*80)
    print(f"\n📊 Rapports générés:")
    print(f"   - monitoring_report.html")
    print(f"   - monitoring_tests.json")
    print(f"   - performance_report.html")
    print(f"   - performance_metrics.json")


if __name__ == "__main__":
    main()