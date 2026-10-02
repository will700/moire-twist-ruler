"""Benchmark set 2: an STM topograph of 4.3 deg twisted bilayer graphene (rigid moire).

Source: F. Mesple, P. Mallet, G. Trambly de Laissardiere, C. Dutreix, G. Lapertot, J-Y. Veuillen,
V. T. Renard, "Experimental evidence of the topological obstruction in twisted bilayer graphene",
arXiv:2506.08913. Data: Zenodo doi:10.5281/zenodo.17360113, CC BY 4.0.

The image is the 200 mV topograph (the paper's Fig. 1b conditions, Vb = 200 mV), forward Z
channel, plane levelled, 50 x 50 nm at 1008 x 1008 px (from the .sxm header). The reference is the
paper's own reading: "The twist angle, determined from the moire period D = 3.25 nm, is 4.3 deg",
so this set checks the period on a different instrument and a rigid (unrelaxed) moire.

Only that one 24 MB file is read out of the 237 MB zip, with HTTP range requests.

    python benchmark/fetch_mesple_stm.py
"""
import os, io, re, json, zipfile, urllib.request
import numpy as np
from PIL import Image

URL = "https://zenodo.org/records/17360113/files/STM_images.zip?download=1"
MEMBER = "STM_images/SiCCAO#C020_200mV.sxm"
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data", "mesple_stm")

class RangeFile(io.RawIOBase):
    """a seekable read-only view of a remote file, fetched in pieces with HTTP Range requests"""
    def __init__(self, url):
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"Range": "bytes=0-0"}))
        self.url, self.n, self.p = url, int(r.headers["Content-Range"].split("/")[1]), 0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.p
    def seek(self, o, w=0):
        self.p = o if w == 0 else (self.p + o if w == 1 else self.n + o); return self.p
    def readinto(self, b):
        if self.p >= self.n: return 0
        end = min(self.p + len(b), self.n) - 1
        d = urllib.request.urlopen(urllib.request.Request(self.url, headers={"Range": f"bytes={self.p}-{end}"})).read()
        b[:len(d)] = d; self.p += len(d); return len(d)

def read_sxm(raw):
    end = raw.index(b":SCANIT_END:"); head = raw[:end].decode("latin1")
    field = lambda k: re.search(rf":{k}:\n(.*?)\n:", head, re.S).group(1).split()
    nx, ny = map(int, field("SCAN_PIXELS")); rx, ry = map(float, field("SCAN_RANGE"))
    data = np.frombuffer(raw[raw.index(b"\x1a\x04", end) + 2:], dtype=">f4")
    z = data[:nx * ny].reshape(ny, nx)                         # first channel: Z, forward
    if field("SCAN_DIR")[0] == "up": z = z[::-1]
    return z.astype(float), rx * 1e9 / nx, ry * 1e9 / ny

def main():
    os.makedirs(DATA, exist_ok=True); cache = os.path.join(DATA, "C020_200mV.sxm")
    if not os.path.exists(cache):
        z = zipfile.ZipFile(io.BufferedReader(RangeFile(URL), buffer_size=1 << 22))
        open(cache, "wb").write(z.read(MEMBER))
    z, px, py = read_sxm(open(cache, "rb").read())
    ny, nx = z.shape; yy, xx = np.mgrid[:ny, :nx]
    A = np.c_[xx.ravel(), yy.ravel(), np.ones(nx * ny)]
    z = z - (A @ np.linalg.lstsq(A, z.ravel(), rcond=None)[0]).reshape(ny, nx)
    lo, hi = np.percentile(z, [0.5, 99.5])
    fn = "mesple2025_TBG_STM_200mV.png"
    Image.fromarray((np.clip((z - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)).save(os.path.join(DATA, fn), optimize=True)
    row = dict(dataset="mesple_stm", image="C020_200mV", file=f"mesple_stm/{fn}", nm_per_px=px,
               modality="STM topography", material="graphene/graphene (on SiC)", stacking="rigid moire",
               lattice_nm=0.246, poisson_nu=0.16, method="domains",
               ref_twist_deg=4.3, ref_twist_err_deg=float("nan"), ref_heterostrain_pct=float("nan"),
               ref_source="paper: twist from the moire period D = 3.25 nm", field_nm=nx * px, duplicate_of="")
    json.dump([row], open(os.path.join(DATA, "reference.json"), "w"), indent=1)
    print(fn, f"{nx * px:.1f} nm field at {px:.4f} nm/px")

if __name__ == "__main__":
    main()
