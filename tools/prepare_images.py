"""Convert microscope images (dm3, dm4, emd, tif, ...) to PNGs the browser can show,
and write scales.csv (filename, nm_per_px) so Moire Line Ruler sets every scale.

    pip install rosettasciio numpy pillow scipy
    python tools/prepare_images.py OUT_DIR file1.dm3 file2.dm4 ...

Each image is lightly detrended (divided by a broad Gaussian background) and
contrast-stretched to the 0.5-99.5 percentile. The pixel size comes from the file's
own calibration; check it against a known lattice spacing if you can.
"""
import sys, os
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

UNIT_TO_NM = {"nm": 1.0, "µm": 1e3, "um": 1e3, "Å": 0.1, "A": 0.1, "pm": 1e-3, "m": 1e9}

def read(path):
    from rsciio.digitalmicrograph import file_reader as dm
    ext = os.path.splitext(path)[1].lower()
    if ext in (".dm3", ".dm4"):
        d = dm(path, lazy=False)[0]
    elif ext == ".emd":
        from rsciio.emd import file_reader as emd
        d = emd(path, lazy=False)[0]
    elif ext in (".tif", ".tiff"):
        from rsciio.tiff import file_reader as tif
        d = tif(path, lazy=False)[0]
    else:
        raise ValueError(f"unsupported file type {ext}")
    img = np.asarray(d["data"], dtype=float)
    while img.ndim > 2: img = img[0]
    ax = d["axes"][-1]
    k = UNIT_TO_NM.get(str(ax.get("units", "")).strip())
    return img, (ax["scale"] * k if k else None)

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    rows = ["filename,nm_per_px"]
    for p in sys.argv[2:]:
        try:
            img, px = read(p)
        except Exception as e:
            print("skip", p, e); continue
        img[~np.isfinite(img)] = np.nanmedian(img)
        bg = gaussian_filter(img, img.shape[0] / 8)
        d = gaussian_filter(img / np.maximum(bg, 1e-9 * abs(bg).max() + 1e-12), 0.8)
        lo, hi = np.percentile(d, [0.5, 99.5])
        a = (np.clip((d - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        fn = os.path.splitext(os.path.basename(p))[0] + ".png"
        Image.fromarray(a).save(os.path.join(out, fn))
        rows.append(f"{fn},{px:.6g}" if px else f"{fn},")
        print(fn, f"{px:.4g} nm/px" if px else "no calibration found: set it in the page")
    open(os.path.join(out, "scales.csv"), "w").write("\n".join(rows) + "\n")

if __name__ == "__main__":
    main()
