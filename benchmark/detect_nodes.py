"""Label-free node finder for the benchmark. No reference twist or period is used anywhere.

parallel stacking: AA nodes are bright cores about a nm across (their size does not scale with the
  twist), so they are found with a fixed physical filter: a 0.4 nm core against a 0.9-1.5 nm ring
  (run on the 4x upsampled image).
  Peaks are taken strongest first, and the largest set that still forms a regular lattice (most
  points share one nearest-neighbour spacing) is kept: noise peaks break that regularity. The period
  L is the median nearest-neighbour spacing of the kept peaks, and a final pass keeps one peak per
  0.6 L.
antiparallel stacking: the bright hexagonal XMMX domains scale with L, so their size is found with a
  scale-normalised blob filter: at each trial scale the strongest blobs that still form a regular
  lattice spaced at least 3 blob radii apart are kept, and the scale with the strongest such
  lattice wins. At low twist the domains are grey and outlined by thin dark walls instead; then the
  domain centres are the maxima of the distance to the walls. Whichever of the two is more regular is
  used (ties go to the one with more points). The domain centres sit on the moire lattice, and L is again the median nearest-neighbour spacing.
"""
import numpy as np
from scipy import ndimage as nd
from scipy.spatial import cKDTree

def _disk(r0, r1):
    r1 = max(r1, 1.0); n = int(np.ceil(r1)); y, x = np.mgrid[-n:n + 1, -n:n + 1]; d = np.hypot(x, y)
    k = ((d >= r0) & (d <= r1)).astype(float); return k / k.sum()

def _local_max(score, rad):
    mx = nd.maximum_filter(score, size=2 * int(np.ceil(rad / 1.5)) + 1)   # square (fast); exact circular spacing comes from _greedy
    pk = np.argwhere((score == mx) & (score > 0)); v = score[pk[:, 0], pk[:, 1]]
    o = np.argsort(-v); return pk[o][:, ::-1].astype(float), v[o]

def _greedy(P, v, rad):
    """keep the strongest point, drop everything within rad of it, repeat (P sorted strongest first)"""
    if len(P) == 0: return P, v
    tree = cKDTree(P); alive = np.ones(len(P), bool); keep = []
    for i in range(len(P)):
        if not alive[i]: continue
        keep.append(i); alive[tree.query_ball_point(P[i], rad)] = False
    return P[keep], v[keep]

def _two_means(v):
    lv = np.log(np.maximum(v, 1e-9)); t = np.median(lv)
    for _ in range(50):
        a, b = lv[lv <= t], lv[lv > t]
        if not len(a) or not len(b): break
        t2 = (a.mean() + b.mean()) / 2
        if abs(t2 - t) < 1e-6: break
        t = t2
    return np.exp(t)

def _regularity(P):
    if len(P) < 5: return 0.0
    d, _ = cKDTree(P).query(P, k=2); nn = d[:, 1]
    return float(np.mean(np.abs(nn / np.median(nn) - 1) < 0.15))

def _most_regular(P, v, need=0.75, min_nn=0.0):
    """peaks are sorted strongest first; keep the largest top-k set that still forms a regular
    lattice (most points share the same nearest-neighbour spacing) spaced at least min_nn apart.
    Noise peaks break that regularity. k runs over every value up to 400, then a coarse grid."""
    ks = list(range(6, min(len(P), 400) + 1))
    if len(P) > 400: ks += sorted(set(np.geomspace(401, len(P), 40).astype(int)))
    best = min(len(P), 6)
    for k in ks:
        if _regularity(P[:k]) >= need and _nn(P[:k]) >= min_nn: best = k
    return P[:best], v[:best]

DEBUG = []

def _regularity_loose(P):
    """share of points whose nearest neighbour is within 30 % of the median (heterostrained lattices)"""
    if len(P) < 5: return 0.0
    d, _ = cKDTree(P).query(P, k=2); nn = d[:, 1]
    return float(np.mean(np.abs(nn / np.median(nn) - 1) < 0.3))

def _refine(score, P):
    H, W = score.shape; out = []
    for x, y in P:
        x0, y0 = int(round(x)), int(round(y))
        ys, xs = slice(max(0, y0 - 2), min(H, y0 + 3)), slice(max(0, x0 - 2), min(W, x0 + 3))
        w = score[ys, xs].clip(0); yy, xx = np.mgrid[ys, xs]
        out.append((float((w * xx).sum() / w.sum()), float((w * yy).sum() / w.sum())) if w.sum() > 0 else (x, y))
    return np.array(out)

def _nn(P):
    if len(P) < 3: return float("nan")
    d, _ = cKDTree(P).query(P, k=2); return float(np.median(d[:, 1]))

def find_nodes(img, ori, nm_per_px):
    """ori: 'p' / 'aa_nodes' = compact bright AA nodes of a relaxed network;
    'ap' / 'domains' = bright domains or AA spots whose centres sit on the moire lattice"""
    g = img.astype(float); u = 1 / nm_per_px          # px per nm
    if ori in ("p", "aa_nodes"):
        s = nd.gaussian_filter(g, 0.25 * u)
        score = nd.convolve(s, _disk(0, 0.4 * u)) - nd.convolve(s, _disk(0.9 * u, 1.5 * u))
        P, v = _local_max(score, 3.0 * u)
        P, v = _greedy(P, v, 3.0 * u)
        P, v = _most_regular(P, v, min_nn=6.0 * u)          # a lattice, not the 3 nm candidate spacing
        L = _nn(P)
        P, v = _greedy(P, v, 0.6 * L)
    else:
        best = None
        for sig in np.geomspace(0.3 * u, min(g.shape) / 6, 26):
            r = -sig ** 2 * nd.gaussian_laplace(g, sig)
            Pk, vk = _local_max(r, 1.5 * sig); Pk, vk = _greedy(Pk, vk, 1.5 * sig)
            if len(Pk) < 5: continue
            Pk, vk = _most_regular(Pk, vk, need=0.7, min_nn=3.0 * sig)
            if len(Pk) < 5 or _regularity(Pk) < 0.7: continue
            m = float(np.mean(vk))
            if best is None or m > best[0]: best = (m, sig, r, Pk, vk)
        blob = best
        # domains outlined by thin dark walls (low twist): every enclosed region is one domain
        s1 = nd.gaussian_filter(g, 0.5 * u); hp = s1 - nd.gaussian_filter(s1, 8 * u)
        wall = nd.binary_opening(hp < -0.8 * hp.std(), iterations=1)
        lab, nlab = nd.label(~wall)
        dom = None
        if nlab >= 5:
            idx = np.arange(1, nlab + 1); area = nd.sum(np.ones_like(g), lab, idx)
            edge = np.zeros(nlab + 1, bool)
            for side in (lab[0], lab[-1], lab[:, 0], lab[:, -1]): edge[np.unique(side)] = True
            inner = (~edge[1:]) & (area > (2.0 * u) ** 2)
            if inner.sum() >= 4:
                med = np.median(area[inner]); keep = inner & (area > 0.35 * med) & (area < 3 * med)
                cy, cx = np.array(nd.center_of_mass(np.ones_like(g), lab, idx[keep])).T
                Pd = np.stack([cx, cy], 1); vd = area[keep]
                if len(Pd) >= 4: dom = (_regularity_loose(Pd) if len(Pd) >= 5 else 1.0, Pd, vd)
        self_blob = None
        if blob is not None: self_blob = (_regularity_loose(blob[3]), blob[3], blob[4])
        DEBUG.append(dict(blob=None if blob is None else (len(blob[3]), round(self_blob[0], 2), round(_nn(blob[3]), 1)),
                          dom=None if dom is None else (len(dom[1]), round(dom[0], 2), round(_nn(dom[1]), 1))))
        if blob is None and dom is None: return np.zeros((0, 2)), float("nan")
        if dom is not None and (blob is None or (dom[0], len(dom[1])) > (self_blob[0], len(self_blob[1]))):
            _, P, v = dom; return P, _nn(P)            # centroids, no peak refinement
        _, sig, score, P, v = blob
        L = _nn(P)
        P, v = _greedy(P, v, 0.6 * L)
    return _refine(score, P), _nn(P)
