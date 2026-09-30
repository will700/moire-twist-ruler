# Moire Twist Ruler

Measure the moire domain length and twist angle of twisted 2D bilayers by drawing
one line per image. A single HTML page: no install, no server, and your images
never leave your computer.

![relaxed domain network in 0.82 deg twisted bilayer MoS2 (Van Winkle et al. 2023, CC BY 4.0)](examples/vanwinkle2023_DS14_MoS2_parallel.png)

*Example image: virtual dark-field of a 0.82 deg twisted MoS2 bilayer, data from Van Winkle et al. 2023 (CC BY 4.0), see below.*

## Use it

- **Online:** https://will700.github.io/moire-twist-ruler/ (demo with examples: https://will700.github.io/moire-twist-ruler/#examples), or
- **Offline:** download `index.html` and open it in any modern browser.

1. **Open images** (or drag them onto the page). PNG, JPEG and WebP work directly;
   convert microscope files first (below).
2. Set the **pixel size** (nm per pixel) once per image or with *Apply to all*, or drop a
   `scales.csv` (`filename,nm_per_px`) together with the images.
3. Pick the material's **lattice constant** (WS2, MoS2, WSe2, MoSe2, graphene, hBN or custom).
4. **Drag a line** from one domain node (AA site or domain-wall crossing) to another a few
   domains away along a row, and set **periods** to the number of domains it spans. A circle
   marks each period, so you can see at once whether they sit on the nodes.
5. Tick **Don't use this one** for images that should not count (folds, contamination,
   unclear networks).
6. **Download CSV**: one row per image with line length, periods, domain length L,
   twist, and whether to use it. *Save session* keeps your lines in a file to reload later.

Keyboard: left and right arrows change image, `+` and `-` change the period count.

## The maths

L is the AA-to-AA moire period, the line length divided by the number of periods. For
a homobilayer with lattice constant *a* the twist is

    theta = 2 asin(a / 2L)

so L = 18 nm is about 1.0 deg for WS2. Heterobilayers (lattice mismatch) and
heterostrain are not modelled; with strain the three moire directions differ, so draw
along the direction you want to report, or measure a few images and compare.

Measuring across several periods is more precise than one: the error in L shrinks as
1/n.

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
