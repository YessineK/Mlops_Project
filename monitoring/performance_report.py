import json
import os
from datetime import datetime

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

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "performance_metrics.json")
    html_path = os.path.join(base_dir, "performance_report.html")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Performance HTML report saved to {html_path}")

if __name__ == "__main__":
    main()
