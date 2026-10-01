# Details

## The maths

L is the AA-to-AA moire period, the line length divided by the number of periods. For
a homobilayer with lattice constant *a* the twist is

    theta = 2 asin(a / 2L)

so L = 18 nm is about 1.0 deg for WS2. Heterobilayers (lattice mismatch) are
not modelled. Heterostrain is not modelled either, but it shows: the three moire
directions give different periods (L1, L2, L3 in node mode, or lines along different
directions), so report them rather than a single twist when they differ by more than a
few percent.

Measuring across several periods is more precise than one: the error in L shrinks as
1/n.

### Cells, twist and heterostrain (Click nodes mode)

The clicked nodes are joined by a Delaunay triangulation. A triangle counts as a moire
cell when its smallest angle is at least 25 deg, its largest at most 100 deg, and its
area is 0.5 to 1.6 times the median; the rest are slivers at the edge of the clicked area
or triangles across a missing node.

Each cell's sorted sides L1 <= L2 <= L3 are matched exactly to a twisted homobilayer with
uniaxial heterostrain. The top layer is the bottom layer transformed by
T = R(theta) (I + S), with

    S = eps * [[cos^2 psi - nu sin^2 psi, (1 + nu) cos psi sin psi],
               [(1 + nu) cos psi sin psi,  sin^2 psi - nu cos^2 psi]]

(strain eps along psi, Poisson contraction nu across it). The moire lattice is D^-1 B with
D = I - T^-1 and B the atomic basis, so its cell sides follow from (theta, eps, psi); three
sides fix the three unknowns, solved by damped Gauss-Newton from several starts. Only
theta and |eps| are reported: psi is measured from the atomic lattice, which the moire
image does not show. The image result solves the median cell (median of each side); the
error is the standard deviation of the per-cell twists over the square root of the
number of cells, and the 10-90 % range shows real twist variation across the field. nu is
an assumed input (default 0.25). For a synthetic WS2 cell at 1.00 deg with 0.5 % strain
(sides 15.3, 20.2, 20.6 nm) the solved twist is 0.99 to 1.00 deg for nu from 0 to 0.3,
while the pure-twist formula on the mean side gives 0.97 deg. This is the approach of Kerelsky et al., Nature 572,
95 (2019) and Kazmierczak et al., Nature Materials 20, 956 (2021). With equal sides it
reduces to theta = 2 asin(a / 2L).

## Try it on the examples

*Load examples* (when the page is served, e.g. GitHub Pages or `python -m http.server`
in this folder) opens nine images with their pixel sizes; the page shows a reference
twist next to yours so you can check your technique.

**Experimental (open data):** six 4D-STEM Bragg-interferometry dark-field images of
reconstructed twisted MoS2 bilayers, parallel and antiparallel, 0.77 to 1.77 deg
(`examples/vanwinkle2023_*.png`). The reference is the authors' fitted average twist.
Choose MoS2 as the lattice. These cells carry 0.3-0.6 percent heterostrain, so a single
line along one direction can differ from the fitted average by a few percent; that is
real, and a good reason to draw along a clean row over several periods.

> Data from M. Van Winkle, I. M. Craig, S. Carr, M. Dandu, K. C. Bustillo, J. Ciston,
> C. Ophus, T. Taniguchi, K. Watanabe, A. Raja, S. Griffin and D. K. Bediako,
> "Rotational and dilational reconstruction in transition metal dichalcogenide moire
> bilayers", *Nature Communications* **14**, 2989 (2023),
> https://doi.org/10.1038/s41467-023-38504-7. Dataset: https://doi.org/10.5281/zenodo.7779105,
> licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
> Changes: the dark-field images of the disks used by the authors were summed,
> upsampled 4x and contrast-stretched (`tools/fetch_open_examples.py` rebuilds them from Zenodo).

**Synthetic:** three rigid twisted WS2-lattice moires at exactly 1.0, 2.5 and 4.0 deg
(`examples/synthetic_*.png`, made by `tools/make_examples.py`), for a known answer.

To rebuild all examples: `python tools/make_examples.py && python tools/fetch_open_examples.py`.

## Converting microscope files

    pip install rosettasciio numpy pillow scipy
    python tools/prepare_images.py converted/ your_images/*.dm4

This writes one PNG per image (lightly detrended and contrast-stretched) and a
`scales.csv` with the pixel size read from each file's calibration. Open the PNGs and
the CSV together in the page.

## Background

Low-angle twisted bilayers of transition metal dichalcogenides relax into domains of
commensurate stacking separated by domain walls, and the domain period grows as the
twist falls. See Weston et al., "Atomic reconstruction in twisted bilayers of
transition metal dichalcogenides", Nature Nanotechnology 15, 592 (2020),
https://doi.org/10.1038/s41565-020-0682-9 (preprint: https://arxiv.org/abs/1911.12664).
The experimental examples are the openly licensed Van Winkle et al. data above; no
other experimental data is included in this repository.

## Privacy

Everything runs in your browser. Images are read locally and are not uploaded or
stored; only your lines, pixel sizes and settings are kept in the browser's local
storage (per image name) so you can close the tab and continue later. Clear them with
your browser's site-data settings.

## Licence

Code: MIT (see LICENSE). The experimental example images in `examples/vanwinkle2023_*`
are derived from data licensed CC BY 4.0 by their authors (credit above); they are
not covered by the MIT licence.
