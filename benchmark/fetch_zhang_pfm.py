"""Benchmark set 3: human-clicked moire sites and their published cell fits (solver check).

Source: Q. Zhang, L. Lyu, S. Pancholi et al., "Dynamic twisting and imaging of moire crystals",
arXiv:2307.06997. Data: Zenodo doi:10.5281/zenodo.20939203, CC BY 4.0.

The deposit has PFM images of a twisted graphene rotor and a twisted MoTe2 rotor, the moire site
coordinates the authors extracted from each image (nm), and their own per-triangle fit of twist and
uniaxial heterostrain (rows alpha, eps %, phi, theta in rad; lattice 0.246 nm and Poisson ratio 0.16
for graphene, 0.3551 nm and 0.25 for MoTe2, from their notebooks). The PFM images carry no pixel
size, so they are not used; this set feeds the authors' own clicks to the ruler's cell solver and
compares the result with their independent fit. It tests the solver, not node finding.

    python benchmark/fetch_zhang_pfm.py            (14 MB download)
"""
import os, io, json, zipfile, urllib.request
import numpy as np

URL = "https://zenodo.org/records/20939203/files/Dynamic-twisting-and-imaging-of-moire-crystals.zip?download=1"
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data", "zhang_pfm")
ROOT = "Dynamic-twisting-and-imaging-of-moire-crystals/Data_for_upload/Data/"
SETS = [("graphene", "Graphene rotor", "fit_result/PFM_fit_result{}_checked.csv", 0.246, 0.16),
        ("MoTe2", "MoTe2 rotor", "fit result/MoTe_parameter{}.csv", 0.3551, 0.25)]

def main():
    os.makedirs(DATA, exist_ok=True); cache = os.path.join(DATA, "deposit.zip")
    if not os.path.exists(cache): open(cache, "wb").write(urllib.request.urlopen(URL, timeout=300).read())
    z = zipfile.ZipFile(cache); rows = []
    rd = lambda p: np.loadtxt(io.StringIO(z.read(ROOT + p).decode()), delimiter=",", ndmin=2)
    for mat, folder, fit, a, nu in SETS:
        for i in range(1, 5):
            P = rd(f"{folder}/coordinate/PFM{i}.csv"); F = rd(f"{folder}/{fit.format(i)}")
            th = np.degrees(np.abs(F[3])); eps = np.abs(F[1])
            rows.append(dict(dataset="zhang_pfm", image=f"{mat}_PFM{i}", file="", nm_per_px=1.0, modality="PFM (site coordinates)",
                             material=f"{mat}/{mat}", stacking="parallel", lattice_nm=a, poisson_nu=nu, method="given_nodes",
                             ref_twist_deg=float(th.mean()), ref_twist_err_deg=float(th.std(ddof=1) / np.sqrt(len(th))),
                             ref_heterostrain_pct=float(eps.mean()), ref_source=f"authors' per-triangle fit, mean of {F.shape[1]} triangles",
                             field_nm=float(np.ptp(P[:, 0])), duplicate_of="", nodes=P.tolist(), ref_triangles=int(F.shape[1])))
            print(rows[-1]["image"], len(P), "sites,", F.shape[1], f"fitted triangles, mean twist {th.mean():.3f} deg")
    json.dump(rows, open(os.path.join(DATA, "reference.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
