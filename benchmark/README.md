# Benchmark: the ruler against published twist angles

The ruler measures the moire period from clicked nodes and solves each triangular cell for twist
and heterostrain. This folder checks it against every public dataset we could find that has real
images of twisted bilayers **and** an independently published twist angle, under an open licence.

## Results

Twist error = ruler minus published value. Images marked fail in the visual check, and the two
duplicated images, are left out; partial ones are kept. Full table: `results/auto/results.csv`;
every node set drawn on its image: `results/auto/overlays/`.

| group | images | median abs error | mean error | RMS | max abs | median abs relative |
|---|---|---|---|---|---|---|
| Van Winkle 2023, MoS2, parallel: relaxed triangles, automatic AA nodes | 14 | 0.016 deg | +0.027 deg | 0.048 deg | 0.143 deg | 1.4 % |
| Van Winkle 2023, MoS2, antiparallel: hexagonal domains, automatic domain centres | 9 | 0.044 deg | +0.034 deg | 0.071 deg | 0.157 deg | 2.3 % |
| Mesple 2025, graphene, STM: rigid moire, automatic AA spots | 1 | 0.175 deg | +0.175 deg | | | 4.1 % |
| **all images (node finding and solver)** | **24** | **0.031 deg** | **+0.036 deg** | **0.067 deg** | **0.175 deg** | **2.2 %** |
| Zhang 2024, graphene and MoTe2, PFM: the authors' own clicked sites (solver only) | 7 | 0.001 deg | +0.000 deg | 0.001 deg | 0.003 deg | 0.1 % |

Heterostrain from the cell solver against the published values: median difference 0.075
percentage points on Van Winkle (23 images, published 0.14 to 1.32 %), 0.003 on Zhang (7).

What this says:

- **The solver reproduces published cell fits.** Given the same clicked sites as Zhang et al., it
  matches their own independent twist and heterostrain fit to 0.003 deg and 0.01 % on all seven
  usable images (0.29 to 0.60 deg, two materials).
- **From the image alone it lands within a few hundredths of a degree** of 4D-STEM Bragg
  interferometry fits, over 0.37 to 2.56 deg, parallel and antiparallel, with 5 to 64 nodes. The
  largest misses are on the most strained images (DS11, 1.3 % heterostrain; DS17, 1.1 %), where the
  automatic nodes are patchy. The errors lean slightly high (+0.03 deg on average).
- **The STM image reads 4 % high.** The ruler measures a mean period of 3.16 nm on the 50 nm scan
  (309 AA spots, 542 cells, calibration from the file header); the paper quotes D = 3.25 nm and
  "4.3 deg" for this sample without saying how D was read. The 3 % gap is in the period, not in the
  twist formula.
- Automatic node finding is a stand-in for a person clicking and is the weak part: it fails on the
  lowest-twist antiparallel image (DS18, about 1.5 periods across the field). Hand clicks can be
  scored the same way (below), and that is the real test of the tool.


## What is scored

Every node set goes through the ruler's own cell solver (`cells()` in `index.html`, run headless by
`solve_with_page.mjs`), so the numbers are exactly what the page would show. The node sets come from
three places:

- **Automatic nodes** (`detect_nodes.py`) on the calibrated images. The detector never sees the
  reference values: its only length scales are physical (an AA node is a bright core about a nm
  across, whatever the twist) or come from the image itself, and it keeps the largest set of points
  that forms a regular lattice. Parallel (relaxed) networks: the bright AA nodes. Antiparallel
  networks and rigid moires: the centres of the bright domains or AA spots, which sit on the same
  lattice. This stands in for a person clicking, so a row is a test of detection and solver together.
- **The authors' own clicked sites** (Zhang 2024): their published site coordinates go straight into
  the solver and are compared with their own independent cell fits. This tests the solver alone.
- **Your clicks**: open the benchmark images in the ruler, click, save the session and score it (below).

Every automatic node set is drawn over its image in `results/auto/overlays/`, and each image has a
visual check in `qc_auto.csv` (ok / partial / fail, with a note). Images marked fail and the two
duplicated images are left out of the summary; they stay in `results/auto/results.csv`.

## Datasets

Searched (2 October 2026): Zenodo, Figshare, Materials Data Facility, NOMAD, Materials Cloud,
Dryad, OSF, Harvard Dataverse, 4TU.ResearchData, Stanford Digital Repository, Hugging Face, GitHub,
and the data statements of the main twisted-bilayer imaging papers.

**Used** (open licence, real images or sites, published twist per image):

| set | what | images | reference | licence |
|---|---|---|---|---|
| Van Winkle et al., Nat. Commun. 14, 2989 (2023), [doi:10.5281/zenodo.7779105](https://doi.org/10.5281/zenodo.7779105) | 4D-STEM Bragg interferometry, summed virtual dark field; MoS2/MoS2, 14 parallel and 12 antiparallel, 50 or 100 nm fields at 0.5 nm/px | 26 (DS19 and DS20 repeat the pixels of DS17 and DS18) | authors' fit per set: twist +- error, heterostrain (`info.txt`) | CC BY 4.0 |
| Mesple et al., [arXiv:2506.08913](https://arxiv.org/abs/2506.08913), [doi:10.5281/zenodo.17360113](https://doi.org/10.5281/zenodo.17360113) | STM topography of twisted bilayer graphene on SiC, 50 nm at 1008 px (the 200 mV frame, Fig. 1b conditions) | 1 | paper: 4.3 deg from the moire period D = 3.25 nm | CC BY 4.0 |
| Zhang, Lyu, Pancholi et al., [arXiv:2307.06997](https://arxiv.org/abs/2307.06997), [doi:10.5281/zenodo.20939203](https://doi.org/10.5281/zenodo.20939203) | PFM of a graphene rotor and a MoTe2 rotor: the moire sites the authors extracted (nm) and their per-triangle twist and heterostrain fits | 8 site sets (no pixel size on the images, so the sites are scored, not the images) | authors' per-triangle fits | CC BY 4.0 |

**Found but not benchmarked**, and why:

| set | why not |
|---|---|
| Van Winkle 2023 DS28-DS37 (WSe2/MoS2) | heterobilayers: the 4 % lattice mismatch sets the period, which the ruler does not model; most have no twist fit |
| Kazmierczak et al., Nat. Mater. 2021, twisted bilayer graphene (19 Zenodo records, e.g. [4459671](https://zenodo.org/records/4459671)) | raw 4D-STEM only, 4 to 34 GB per scan (551 GB in all), no real-space calibration in the files; twist per scan is given, so it is the best next step |
| Tran et al., APL 125, 113106 (2024), [Stanford SDR ym579qg7863](https://purl.stanford.edu/ym579qg7863) | torsional force microscopy of near-magic-angle graphene, 26 raw Bruker scans (2 GB); twist and strain per scan come from the authors' processed pickles, not yet unpacked |
| de Jong et al., Nat. Commun. 2022, LEEM, [4TU 10.4121/16843510](https://doi.org/10.4121/16843510) | huge 0.1 deg networks (57 and 154 MB stitched images), but the twist is a local map from their analysis code, not a value per image |
| Ko et al., Nat. Mater. 2023, [doi:10.5281/zenodo.7956290](https://doi.org/10.5281/zenodo.7956290); Van Winkle et al., Nat. Nano. 2024, [doi:10.5281/zenodo.10697963](https://doi.org/10.5281/zenodo.10697963) | calibrated dark-field TEM of twisted WSe2 bi- and trilayers, but no twist per image (only plots or per-region values in the papers) |
| Craig et al., Nat. Mater. 2024, [doi:10.5281/zenodo.4459669](https://doi.org/10.5281/zenodo.4459669) | twisted graphene trilayers (two interfering moires); twists only in the paper |
| Chiodini et al. 2026, AFM of twisted hBN, [doi:10.5281/zenodo.21626883](https://doi.org/10.5281/zenodo.21626883); Wang et al. 2022 and Yasuda et al. 2021 PFM/AFM, Harvard Dataverse | one twist per sample (or "near 0 deg"), no pixel size in some files |
| STM sets of magic-angle graphene (Zenodo 8317363, 5173159) and twisted WS2 (Dataverse QHJCBQ) | fields of 10 to 25 nm: two periods or fewer |
| simulated relaxed structures: 2D Mater. 2023 MoS2 ([7243735](https://doi.org/10.5281/zenodo.7243735)), Ahmed and Admal heterostrain cases ([Materials Cloud](https://archive.materialscloud.org/records/vsv00-8vy33)), Warwick MLIP TMD bilayers (CC BY-NC) | exact twist and strain, but atoms, not images; the obvious next step for a ground-truth set with known heterostrain |
| papers whose data is on request or unpublished | Weston 2020 and 2022, Yoo 2019, Andersen 2021, Rosenberger 2020, McGilly 2020, Kerelsky 2019 and others |

Only derived numbers, the fetch scripts and small overlays are kept in this repository; the images
are rebuilt from the sources by the fetch scripts. Credit for the data goes to the authors above.

## Reproduce

```
python benchmark/fetch_vanwinkle2023.py      # 60 MB from Zenodo, cached in benchmark/data (git-ignored)
python benchmark/fetch_mesple_stm.py         # one 24 MB file read out of a 237 MB zip
python benchmark/fetch_zhang_pfm.py          # 14 MB
npm install --prefix benchmark               # puppeteer-core; uses your installed Chrome or Chromium
python benchmark/run_benchmark.py            # -> benchmark/results/auto/
```

Python needs numpy, scipy and pillow. Set `CHROME=/path/to/chrome` if Chrome is not found.

## Score your own clicks

```
python -m http.server                        # from the repository root
# open http://localhost:8000/index.html?manifest=benchmark/data/manifest.json
# Measure by: Click nodes (or Lines), measure each image, then Save session
python benchmark/run_benchmark.py --session moire_ruler_session.json --tag mine
```

Results go to `benchmark/results/mine/`: the node cells scored by the page's solver, and for images
with lines the pure-twist value from their mean L, each next to the published twist.
