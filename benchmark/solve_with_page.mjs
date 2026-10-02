// Score node sets with the ruler's own cell solver (index.html, run headless).
//   node solve_with_page.mjs jobs.json results.json [path/to/index.html]
// jobs.json: [{name, w, h, nm_per_px, a_nm, nu, nodes: [[x, y], ...]}]  (image px)
import puppeteer from "puppeteer-core"; import fs from "node:fs"; import path from "node:path";
const [jobsF, outF, page_ = "../../index.html"] = process.argv.slice(2);
const jobs = JSON.parse(fs.readFileSync(jobsF));
const exe = process.env.CHROME || ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].find(p => fs.existsSync(p));
const b = await puppeteer.launch({ executablePath: exe, headless: true });
const p = await b.newPage(); const errs = []; p.on("pageerror", e => errs.push(e.message));
await p.goto("file://" + path.resolve(page_), { waitUntil: "load" });
const res = await p.evaluate(jobs => jobs.map(j => {
  const im = { name: j.name, w: j.w, h: j.h, img: null, scale: j.nm_per_px, trueTwist: NaN };
  IM.push(im); store.a = "custom"; store.aCustom = String(j.a_nm); store.nu = j.nu;
  line(im).nodes = j.nodes.map(q => [+q[0].toFixed(1), +q[1].toFixed(1)]);
  const c = cells(im);
  if (!c || !c.n) return { name: j.name, nodes: j.nodes.length, cells: 0 };
  return { name: j.name, nodes: c.nodes, cells: c.n, triangles: c.all.length, L_nm: c.L, L1: c.Lm[0], L2: c.Lm[1], L3: c.Lm[2],
    twist: c.th, twist_err: c.thErr, twist_sd: c.thSd, twist_p10: c.thLo, twist_p90: c.thHi, heterostrain_pct: c.eps, pure_twist: c.pure };
}), jobs);
fs.writeFileSync(outF, JSON.stringify(res, null, 1));
console.log(`${res.length} jobs scored`, errs.length ? errs : "");
await b.close();
