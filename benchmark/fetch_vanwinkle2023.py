"""Benchmark set 1: every twisted MoS2 homobilayer in Van Winkle et al. 2023.

Source: M. Van Winkle, I. M. Craig, S. Carr, M. Dandu, K. C. Bustillo, J. Ciston, C. Ophus,
T. Taniguchi, K. Watanabe, A. Raja, S. Griffin, D. K. Bediako, "Rotational and dilational
reconstruction in transition metal dichalcogenide moire bilayers", Nat. Commun. 14, 2989 (2023).
Data: Zenodo doi:10.5281/zenodo.7779105, CC BY 4.0.

The record holds 36 Bragg interferometry (4D-STEM) sets. DS1-DS26 are MoS2/MoS2 homobilayers
(DS1-DS14 parallel, DS15-DS26 antiparallel); DS28-DS37 are WSe2/MoS2 heterobilayers, which are
skipped (their period is set mostly by the 4 % lattice mismatch, which the ruler does not model,
and most have no twist fit). Each image is the sum of the virtual dark-field images of the Bragg
disks the authors used, upsampled 4x, exactly as in tools/fetch_open_examples.py. The reference
values are the authors' fits in each set's info.txt (AvgMoireTwist +- ErrMoireTwist,
AvgHeteroStrain, PoissonRatio).

    python benchmark/fetch_vanwinkle2023.py        (about 60 MB download, cached in benchmark/data)
"""
import os, io, re, sys, json, hashlib, zipfile, urllib.request
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from fetch_open_examples import SafeUnpickler          # restricted unpickler: no code from the files runs

REC = "https://zenodo.org/records/7779105/files/{}.zip?download=1"
DATA = os.path.join(HERE, "data", "vanwinkle2023"); CACHE = os.path.join(DATA, "zips")
UP = 4

def get(name):
    os.makedirs(CACHE, exist_ok=True); p = os.path.join(CACHE, name + ".zip")
    if not os.path.exists(p):
        open(p, "wb").write(urllib.request.urlopen(REC.format(name), timeout=300).read())
    return zipfile.ZipFile(p)

def main():
    os.makedirs(DATA, exist_ok=True); rows = []; seen = {}
    for i in range(1, 27):
        n = f"DS{i}"; z = get(n)
        info = z.read(f"{n}/info.txt").decode()
        val = lambda k: re.search(rf"^{k}\s*:\s*([^\s#]+)", info, re.M).group(1)
        st = SafeUnpickler(io.BytesIO(z.read(f"{n}/diskset.pkl"))).load()._state
        df, use = np.asarray(st["_df"], float), np.asarray(st["_in_use"]).astype(bool)
        img = df[use].sum(0); px = float(val("PixelSize"))
        digest = hashlib.sha1(img.tobytes()).hexdigest()
        lo, hi = np.percentile(img, [0.5, 99.5])
        a = (np.clip((img - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        stack = "parallel" if val("Orientation").lower() == "p" else "antiparallel"
        fn = f"vanwinkle2023_{n}_MoS2_{stack}.png"
        Image.fromarray(a).resize((a.shape[1] * UP, a.shape[0] * UP), Image.BICUBIC).save(os.path.join(DATA, fn), optimize=True)
        rows.append(dict(dataset="vanwinkle2023", image=n, file=f"vanwinkle2023/{fn}", nm_per_px=px / UP,
                         modality="4D-STEM virtual dark field (Bragg interferometry)", material="MoS2/MoS2", stacking=stack,
                         lattice_nm=float(val("LatticeConstant")), poisson_nu=float(val("PoissonRatio")),
                         method="aa_nodes" if stack == "parallel" else "domains",
                         ref_twist_deg=float(val("AvgMoireTwist")), ref_twist_err_deg=float(val("ErrMoireTwist")),
                         ref_heterostrain_pct=float(val("AvgHeteroStrain")), ref_source="authors' fit (info.txt AvgMoireTwist)",
                         field_nm=a.shape[1] * px, duplicate_of=seen.get(digest, "")))
        seen.setdefault(digest, n)
        print(fn, f"{a.shape[1] * px:.0f} nm field, published twist {rows[-1]['ref_twist_deg']:.3f} deg",
              f"(same pixels as {rows[-1]['duplicate_of']})" if rows[-1]["duplicate_of"] else "")
    json.dump(rows, open(os.path.join(DATA, "reference.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
