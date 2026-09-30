"""Build the experimental example images from an openly licensed dataset.

Source: M. Van Winkle, I. M. Craig, S. Carr, M. Dandu, K. C. Bustillo, J. Ciston,
C. Ophus, T. Taniguchi, K. Watanabe, A. Raja, S. Griffin, D. K. Bediako,
"Rotational and dilational reconstruction in transition metal dichalcogenide moire
bilayers", Nature Communications 14, 2989 (2023), doi:10.1038/s41467-023-38504-7.
Data: Zenodo, doi:10.5281/zenodo.7779105, licence CC BY 4.0.

Each set holds virtual dark-field images of the Bragg disks from a 4D-STEM scan
(Bragg interferometry). This script sums the dark-field images of the disks the
authors used, which shows the relaxed domain network (dark walls, bright AA nodes),
upsamples 4x (bicubic) for comfortable drawing, stretches the contrast, and writes
PNGs plus the pixel size and the authors' fitted average twist (info.txt,
AvgMoireTwist) as the reference value.

The pickles are read with a restricted unpickler: only numpy arrays and built-in
containers are rebuilt, every other class becomes an inert placeholder, so no code
from the files is executed.

    pip install numpy pillow
    python tools/fetch_open_examples.py
"""
import os, io, re, pickle, zipfile, urllib.request
import numpy as np
from PIL import Image

REC = "https://zenodo.org/records/7779105/files/{}.zip?download=1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples")
SETS = ["DS14", "DS13", "DS25", "DS7", "DS22", "DS5"]
UP = 4

class _Inert:
    def __init__(self, *a, **k): pass
    def __setstate__(self, st): self.__dict__["_state"] = st

class SafeUnpickler(pickle.Unpickler):
    SAFE = {("builtins", n) for n in ("list", "dict", "tuple", "set", "frozenset", "int", "float", "complex", "str", "bytes", "bool", "slice", "range")}
    def find_class(self, mod, name):
        if mod.split(".")[0] == "numpy" or (mod, name) in self.SAFE or (mod == "_codecs" and name == "encode"):
            return super().find_class(mod, name)
        return type(name, (_Inert,), {"__module__": "inert." + mod})

def load_set(name):
    raw = urllib.request.urlopen(REC.format(name), timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    info = z.read(f"{name}/info.txt").decode()
    st = SafeUnpickler(io.BytesIO(z.read(f"{name}/diskset.pkl"))).load()._state
    df, use = np.asarray(st["_df"], float), np.asarray(st["_in_use"]).astype(bool)
    val = lambda k: re.search(rf"^{k}\s*:\s*([^\s#]+)", info, re.M).group(1)
    return df[use].sum(0), float(val("PixelSize")), float(val("AvgMoireTwist")), val("Orientation").strip().upper()

def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for s in SETS:
        img, px, tw, orient = load_set(s)
        lo, hi = np.percentile(img, [0.5, 99.5])
        a = (np.clip((img - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        im = Image.fromarray(a).resize((a.shape[1] * UP, a.shape[0] * UP), Image.BICUBIC)
        stack = "parallel" if orient == "P" else "antiparallel"
        fn = f"vanwinkle2023_{s}_MoS2_{stack}.png"
        im.save(os.path.join(OUT, fn), optimize=True)
        rows.append(dict(file=fn, nm_per_px=round(px / UP, 6), true_twist_deg=round(tw, 3),
                         ref_label=f"published fit, Van Winkle et al. 2023 {s}", lattice_nm=0.315,
                         source="doi:10.5281/zenodo.7779105 (CC BY 4.0)"))
        print(fn, f"{a.shape[0] * px:.0f} nm field, published twist {tw:.3f} deg")
    return rows

if __name__ == "__main__":
    import json
    rows = main()
    p = os.path.join(OUT, "manifest.json")
    man = [m for m in json.load(open(p)) if not m["file"].startswith("vanwinkle")] if os.path.exists(p) else []
    for m in man: m.setdefault("ref_label", "synthetic ground truth")
    json.dump(rows + man, open(p, "w"), indent=1)
    with open(os.path.join(OUT, "scales.csv"), "w") as f:
        f.write("filename,nm_per_px,true_twist_deg\n")
        for m in man + rows: f.write(f"{m['file']},{m['nm_per_px']},{m['true_twist_deg']}\n")
