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

# On accepte 2 noms possibles pour la target
TARGET_CANDIDATES = ["churn", "Attrition_Flag"]


# =========================
# PERFORMANCE PART
# =========================
def find_target_column(df: pd.DataFrame):
    for col in TARGET_CANDIDATES:
        if col in df.columns:
            return col
    return None


def compute_metrics(df: pd.DataFrame, target_col: str):
    y_true = df[target_col].astype(int)
    y_pred = df[PRED].astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

    # AUC seulement si proba dispo
    if PROBA in df.columns and df[PROBA].notna().any():
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, df[PROBA].astype(float)))
        except Exception:
            metrics["roc_auc"] = None
    else:
        metrics["roc_auc"] = None

    return metrics


def fmt(x, nd=3):
    if x is None:
        return "—"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def delta_class(d):
    if d is None:
        return "neutral"
    return "bad" if d < 0 else "good"


def build_performance_html(data: dict) -> str:
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
# DRIFT PART (YOUR WORKING CODE)
# =========================
def run_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame, base_dir: str):
    """
    - Evidently Report HTML (new API)
    - Evidently TestSuite JSON (legacy)
    """

    # ---- Report API imports (exactly like your code) ----
    # (Certain Evidently versions use "from evidently import Report" & "from evidently.presets import ...")
    from evidently import Report
    from evidently.presets import DataDriftPreset, DataSummaryPreset

    # ---- Legacy TestSuite imports (fallback tolerant) ----
    try:
        from evidently.legacy.test_suite import TestSuite
    except Exception:
        from evidently.legacy.tests import TestSuite  # fallback

    try:
        from evidently.legacy.test_preset import DataDriftTestPreset
    except Exception:
        from evidently.legacy.test_presets import DataDriftTestPreset  # fallback

    from evidently.legacy.pipeline.column_mapping import ColumnMapping

    # Drop IDs
    for df in (reference_data, current_data):
        df.drop(columns=["CLIENTNUM", "Unnamed: 21"], errors="ignore", inplace=True)

    print("Generating Data Drift Report...")

    metrics = [
        DataDriftPreset(),
        DataSummaryPreset(),
    ]

    report = Report(metrics=metrics)
    snapshot = report.run(current_data=current_data, reference_data=reference_data)

    report_path = os.path.join(base_dir, "monitoring_report.html")
    snapshot.save_html(report_path)
    print(f"✅ Drift HTML saved to {report_path}")

    # ---- TestSuite (legacy) ----
    print("Running Drift Test Suite...")

    column_mapping = ColumnMapping()

    # target for tests: choose existing target in data
    target_col = find_target_column(reference_data)
    if target_col is not None:
        column_mapping.target = target_col

    tests = TestSuite(tests=[DataDriftTestPreset()])
    tests.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)

    json_path = os.path.join(base_dir, "monitoring_tests.json")
    tests.save_json(json_path)
    print(f"✅ Drift tests JSON saved to {json_path}")

    try:
        test_results = tests.as_dict()
        failed = test_results.get("summary", {}).get("failed_tests", 0)
        if failed > 0:
            print(f"⚠️  WARNING: {failed} drift tests failed!")
        else:
            print("✅ All drift tests passed.")
    except Exception:
        print("⚠️ Could not read drift tests summary (but JSON is saved).")


# =========================
# MAIN (COMBINED)
# =========================
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    ref_path = os.path.join(data_dir, "reference_data.csv")
    cur_path = os.path.join(data_dir, "current_data.csv")

    if not os.path.exists(ref_path) or not os.path.exists(cur_path):
        print("❌ Error: Data files not found. Run prepare_data.py first.")
        return

    print("Loading data...")
    reference_data = pd.read_csv(ref_path)
    current_data = pd.read_csv(cur_path)

    print(f"Reference shape: {reference_data.shape}")
    print(f"Current shape: {current_data.shape}")

    # 1) DRIFT
    run_drift(reference_data.copy(), current_data.copy(), base_dir)

    # 2) PERFORMANCE (only if score columns exist)
    print("\n=== PERFORMANCE MONITORING ===")
    if PRED not in reference_data.columns or PRED not in current_data.columns:
        print("❌ Missing 'prediction' column. Run score_data.py first to add prediction/proba.")
        return

    target_ref = find_target_column(reference_data)
    target_cur = find_target_column(current_data)

    if target_ref is None or target_cur is None:
        print(f"❌ Missing target column. Need one of: {TARGET_CANDIDATES}")
        print("   (Your data must contain churn/Attrition_Flag).")
        return

    # (Optional) ensure same target col name used
    target_col = target_ref

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

    alerts = []
    if result["current"]["accuracy"] < 0.75:
        alerts.append("ALERT: accuracy < 0.75")
    if result["current"]["f1"] < 0.60:
        alerts.append("ALERT: f1 < 0.60")
    if result["delta"]["accuracy"] is not None and result["delta"]["accuracy"] < -0.05:
        alerts.append("ALERT: accuracy dropped by more than 0.05")
    result["alerts"] = alerts

    metrics_json_path = os.path.join(base_dir, "performance_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Performance metrics saved to {metrics_json_path}")

    html_path = os.path.join(base_dir, "performance_report.html")
    html = build_performance_html(result)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Performance HTML report saved to {html_path}")

    if alerts:
        print("⚠️ Alerts:")
        for a in alerts:
            print(" -", a)
    else:
        print("✅ No performance alerts.")

    print("\n✅ DONE (drift + performance).")


if __name__ == "__main__":
    main()
