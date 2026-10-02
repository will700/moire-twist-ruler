"""Score the ruler against published twist angles.

    python benchmark/fetch_vanwinkle2023.py; python benchmark/fetch_mesple_stm.py; python benchmark/fetch_zhang_pfm.py
    npm install --prefix benchmark                 (puppeteer-core, to run index.html headless)
    python benchmark/run_benchmark.py              automatic nodes (detect_nodes.py) -> results/auto
    python benchmark/run_benchmark.py --session moire_ruler_session.json --tag mine
                                                   your own clicks/lines from the ruler -> results/mine

Every node set is scored by the ruler's own cell solver (cells() in index.html, run headless by
solve_with_page.mjs), so the numbers are what the page shows. Lines in a session are scored the
way the page scores them (mean L of the lines, pure twist).

To label the benchmark images by hand: serve the repository root (python -m http.server) and open
index.html?manifest=benchmark/data/manifest.json, set Click nodes and click, then Save session.
"""
import os, sys, json, csv, glob, math, argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data")
sys.path.insert(0, HERE)

def load_refs():
    rows = []
    for p in sorted(glob.glob(os.path.join(DATA, "*", "reference.json"))): rows += json.load(open(p))
    if not rows: sys.exit("no data yet: run the fetch_*.py scripts first")
    return rows

def write_manifest(rows):
    man = [dict(file=r["file"], nm_per_px=r["nm_per_px"], true_twist_deg=round(r["ref_twist_deg"], 4),
                ref_label=r["ref_source"], source=f"benchmark set {r['dataset']}") for r in rows if r["file"]]
    json.dump(man, open(os.path.join(DATA, "manifest.json"), "w"), indent=1)

def overlay(r, P, out, cells_ok=None):
    im = Image.open(os.path.join(DATA, r["file"])).convert("RGB"); d = ImageDraw.Draw(im)
    w = max(2, im.width // 300)
    if len(P) >= 3:
        from scipy.spatial import Delaunay
        nn = np.median(np.sort(np.hypot(*(P[:, None] - P[None]).transpose(2, 0, 1)), 1)[:, 1])
        for t in Delaunay(P).simplices:
            for a, b in ((0, 1), (1, 2), (0, 2)):
                if np.hypot(*(P[t[a]] - P[t[b]])) < 1.6 * nn: d.line([tuple(P[t[a]]), tuple(P[t[b]])], fill=(255, 200, 0), width=w)
    rr = 2.5 * w
    for x, y in P: d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 60, 0), width=w)
    im.thumbnail((600, 600)); im.save(out, quality=85)

def lines_twist(segs, k, a):
    Ls = [math.hypot(g["x1"] - g["x0"], g["y1"] - g["y0"]) * k / (g.get("n") or 1) for g in segs]
    L = sum(Ls) / len(Ls); return L, 2 * math.degrees(math.asin(min(a / (2 * L), 1)))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--session"); ap.add_argument("--tag", default=None)
    ap.add_argument("--page", default=os.path.join(HERE, "..", "index.html")); args = ap.parse_args()
    tag = args.tag or ("auto" if not args.session else "session")
    out = os.path.join(HERE, "results", tag); os.makedirs(os.path.join(out, "overlays"), exist_ok=True)
    rows = load_refs(); write_manifest(rows)
    sess = json.load(open(args.session)).get("lines", {}) if args.session else None
    sess = (sess.get("store", {}) or {}).get("lines", sess) if sess and "store" in sess else sess
    jobs, line_res = [], {}
    for r in rows:
        key = f"{r['dataset']}/{r['image']}"; w = h = 0
        if r["method"] == "given_nodes":
            if sess is not None: continue                      # site coordinates only: nothing to click
            P = np.array(r["nodes"]); w, h = P.max(0) + 10
        else:
            im = Image.open(os.path.join(DATA, r["file"])); w, h = im.size
            if sess is not None:
                s = sess.get(os.path.basename(r["file"]), {})
                if s.get("segs"):
                    line_res[key] = lines_twist(s["segs"], r["nm_per_px"], r["lattice_nm"]) + (len(s["segs"]),)
                P = np.array(s.get("nodes", []), float).reshape(-1, 2)
            else:
                from detect_nodes import find_nodes
                P, _ = find_nodes(np.asarray(im.convert("L"), float), r["method"], r["nm_per_px"])
            if len(P): overlay(r, P, os.path.join(out, "overlays", f"{r['dataset']}_{r['image']}.jpg"))
        if len(P): jobs.append(dict(name=key, w=float(w), h=float(h), nm_per_px=r["nm_per_px"], a_nm=r["lattice_nm"], nu=r["poisson_nu"], nodes=np.asarray(P).tolist()))
    jf, rf = os.path.join(out, "jobs.json"), os.path.join(out, "solver.json")
    json.dump(jobs, open(jf, "w"))
    subprocess.run(["node", os.path.join(HERE, "solve_with_page.mjs"), jf, rf, os.path.abspath(args.page)], check=True)
    solved = {s["name"]: s for s in json.load(open(rf))}
    qc = {}
    qp = os.path.join(HERE, f"qc_{tag}.csv")
    if os.path.exists(qp): qc = {f"{q['dataset']}/{q['image']}": q for q in csv.DictReader(open(qp))}
    res = []
    for r in rows:
        key = f"{r['dataset']}/{r['image']}"; s = solved.get(key, {}); q = qc.get(key, {})
        o = dict(dataset=r["dataset"], image=r["image"], modality=r["modality"], material=r["material"], stacking=r["stacking"],
                 field_nm=round(r["field_nm"], 1), ref_twist_deg=round(r["ref_twist_deg"], 4),
                 ref_twist_err_deg=None if math.isnan(r["ref_twist_err_deg"]) else round(r["ref_twist_err_deg"], 4),
                 ref_heterostrain_pct=None if math.isnan(r["ref_heterostrain_pct"]) else round(r["ref_heterostrain_pct"], 3),
                 nodes=s.get("nodes", 0), cells=s.get("cells", 0))
        if s.get("cells"):
            o.update(L_nm=round(s["L_nm"], 3), twist_deg=round(s["twist"], 4), twist_p10_p90=f"{s['twist_p10']:.3f}-{s['twist_p90']:.3f}",
                     heterostrain_pct=round(abs(s["heterostrain_pct"]), 3), pure_twist_deg=round(s["pure_twist"], 4),
                     d_twist_deg=round(s["twist"] - r["ref_twist_deg"], 4))
        if key in line_res:
            L, t, n = line_res[key]; o.update(lines=n, lines_L_nm=round(L, 3), lines_twist_deg=round(t, 4), lines_d_twist_deg=round(t - r["ref_twist_deg"], 4))
        o.update(duplicate_of=r["duplicate_of"], qc=q.get("qc", ""), qc_note=q.get("note", ""))
        res.append(o)
    keys = list(dict.fromkeys(k for o in res for k in o))
    with open(os.path.join(out, "results.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, keys); wr.writeheader(); wr.writerows(res)
    summary(res, out)

def summary(res, out):
    lines = []
    def stats(sel, label, col="d_twist_deg"):
        d = np.array([o[col] for o in sel if o.get(col) is not None])
        if not len(d): return
        rel = np.array([o[col] / o["ref_twist_deg"] for o in sel if o.get(col) is not None])
        lines.append(f"| {label} | {len(d)} | {np.median(np.abs(d)):.3f} | {np.mean(d):+.3f} | {np.sqrt(np.mean(d ** 2)):.3f} | "
                     f"{np.max(np.abs(d)):.3f} | {100 * np.median(np.abs(rel)):.1f} % |")
    use = [o for o in res if not o["duplicate_of"] and o["qc"] != "fail"]
    lines += ["| group | n | median abs error (deg) | mean error (deg) | RMS (deg) | max abs (deg) | median abs relative |", "|---|---|---|---|---|---|---|"]
    stats([o for o in use if o["dataset"] == "vanwinkle2023" and o["stacking"] == "parallel"], "Van Winkle 2023, parallel (relaxed triangles, auto nodes)")
    stats([o for o in use if o["dataset"] == "vanwinkle2023" and o["stacking"] == "antiparallel"], "Van Winkle 2023, antiparallel (hexagonal domains, auto domain centres)")
    stats([o for o in use if o["dataset"] == "mesple_stm"], "Mesple 2025, STM, rigid moire (auto AA spots)")
    stats([o for o in use if o["dataset"] == "zhang_pfm"], "Zhang 2024, PFM, authors' own clicked sites (solver only)")
    stats([o for o in use if o["dataset"] != "zhang_pfm"], "all images (detection + solver)")
    stats([o for o in use if o.get("lines_d_twist_deg") is not None], "lines (pure twist from mean L)", "lines_d_twist_deg")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))

if __name__ == "__main__":
    main()
