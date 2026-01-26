# combine_reports.py
import os
import json

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    drift_path = os.path.join(base_dir, "monitoring_report.html")
    perf_path  = os.path.join(base_dir, "performance_report.html")
    out_path   = os.path.join(base_dir, "combined_report.html")

    if not os.path.exists(drift_path):
        raise FileNotFoundError(f"Missing: {drift_path}")
    if not os.path.exists(perf_path):
        raise FileNotFoundError(f"Missing: {perf_path}")

    drift_html = read_text(drift_path)
    perf_html  = read_text(perf_path)

    # Safe JS string embedding
    drift_js = json.dumps(drift_html)
    perf_js  = json.dumps(perf_html)

    combined = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Monitoring (Drift + Performance)</title>
  <style>
    /* Wrapper only (does NOT change embedded reports) */
    html, body {{
      height: 100%;
      margin: 0;
      background: #0b0f17;
      font-family: Arial, sans-serif;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 9999;
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      background: rgba(11,15,23,0.92);
      border-bottom: 1px solid rgba(255,255,255,0.10);
      backdrop-filter: blur(6px);
    }}
    .btn {{
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(255,255,255,0.06);
      color: #e8eefc;
      padding: 8px 12px;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
    }}
    .btn.active {{
      background: rgba(255,255,255,0.14);
      border-color: rgba(255,255,255,0.28);
    }}
    .hint {{
      color: rgba(232,238,252,0.75);
      margin-left: auto;
      font-size: 12px;
    }}
    .frame-wrap {{
      height: calc(100% - 52px);
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: 0;
      display: none;
      background: white; /* in case report has transparent bg */
    }}
    iframe.active {{
      display: block;
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <button id="btn-drift" class="btn active" type="button">Data Drift</button>
    <button id="btn-perf" class="btn" type="button">Model Performance</button>
    <div class="hint">1 fichier • 2 pages</div>
  </div>

  <div class="frame-wrap">
    <iframe id="frame-drift" class="active"></iframe>
    <iframe id="frame-perf"></iframe>
  </div>

  <script>
    const driftHTML = {drift_js};
    const perfHTML  = {perf_js};

    const frameDrift = document.getElementById("frame-drift");
    const framePerf  = document.getElementById("frame-perf");

    // Load content as-is (no modification)
    frameDrift.srcdoc = driftHTML;
    framePerf.srcdoc  = perfHTML;

    const btnDrift = document.getElementById("btn-drift");
    const btnPerf  = document.getElementById("btn-perf");

    function show(which) {{
      const drift = which === "drift";
      frameDrift.classList.toggle("active", drift);
      framePerf.classList.toggle("active", !drift);
      btnDrift.classList.toggle("active", drift);
      btnPerf.classList.toggle("active", !drift);
    }}

    btnDrift.addEventListener("click", () => show("drift"));
    btnPerf.addEventListener("click",  () => show("perf"));
  </script>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"✅ Combined report generated: {out_path}")
    print("👉 Open it in your browser.")

if __name__ == "__main__":
    main()
