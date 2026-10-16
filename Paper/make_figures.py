"""Paper figures 1-3: methodology flow diagram, dataset samples and leakage bars.

usage: python Paper/make_figures.py [out_dir]   (default: Paper/figures)
Fig. 2 reads sample images from Pearl_Millet_Dataset/Cache_512, so the dataset must be present.
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageOps
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
INK, MUTED, BLUE, ORANGE = "#1f1f1e", "#6b6a63", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

# ---------------- Fig 1: methodology flow ----------------
fig, ax = plt.subplots(figsize=(10, 7.6), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(x, y, w, h, title, body, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6",
                                fc=fc, ec=INK, lw=0.9))
    ax.text(x + w / 2, y + h - 2.3, title, ha="center", va="top", fontsize=9, weight="bold", color=INK)
    ax.text(x + w / 2, y + h - 6.2, body, ha="center", va="top", fontsize=7.4, color=INK, linespacing=1.35)

def arrow(x0, y0, x1, y1, label=None):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11,
                                 lw=1.1, color=INK, shrinkA=2, shrinkB=2))
    if label:
        ax.text((x0 + x1) / 2 + 0.8, (y0 + y1) / 2, label, fontsize=7, color=MUTED, va="center")

SRC, TGT, MOD, EVA = "#e6effa", "#fdeee6", "#eef6ee", "#f3f1ea"
# row 1: data
box(2, 78, 44, 20, "Source data: Paddy Doctor (rice)",
    "10,407 images, 10 classes\nAudit: MD5 + pHash duplicates, cross-class\nconflicts removed → 10,274 images\nGrouped stratified split 7,323 / 1,483 / 1,468", SRC)
box(54, 78, 44, 20, "Target data: pearl millet (Zenodo)",
    "281 images, 5 classes\nMD5 (−17) and pHash ≤ 4 (−36) → 228 images\nEXIF fix, cache ≤ 512 px\nSpecimen groups: cosine ≥ 0.93 → 124 groups", TGT)
# row 2: init + folds
box(2, 50, 44, 22, "Stage 1: rice pre-training",
    "ConvNeXt-Tiny / ViT-B/16, 10-class head\nAdamW, LLRD 0.8, warm-up + cosine, bf16\nlabel smoothing 0.1, class-weighted CE\nImageNet → rice (15 ep), random → rice (≤100 ep)\nbest checkpoint on rice validation macro-F1", MOD)
box(54, 50, 44, 22, "Evaluation protocol",
    "StratifiedGroupKFold(5) on specimen groups\n(original pHash folds kept for comparison)\nData fractions 10 / 25 / 50 / 100 %\nsampled within class, identical across models\nseeds 0, 1, 2", TGT)
arrow(24, 78, 24, 72.6)
arrow(76, 78, 76, 72.6)
# row 3: init strategies
box(2, 25, 96, 19, "Stage 2: transfer to pearl millet (new 5-class head)",
    "Initialisations:   random   |   ImageNet   |   ImageNet → rice   |   random → rice\n"
    "Policies (ConvNeXt): linear probe, partial fine-tuning, full fine-tuning;  ViT: full fine-tuning\n"
    "Fixed 40 epochs, no checkpoint selection, no tuning on pearl-millet data, 320 px, same augmentation", MOD)
arrow(24, 50, 24, 44.6, "backbone weights")
arrow(76, 50, 76, 44.6, "folds × fractions × seeds")
# row 4: analysis
box(2, 2, 30, 17, "Metrics",
    "macro-F1 (primary), balanced\naccuracy, accuracy, per-class F1,\nECE, NLL, Brier", EVA)
box(35, 2, 30, 17, "Paired statistics",
    "fold-level Δ, d_z, t-interval,\nimage-level bootstrap, Holm,\npre-specified claim rule", EVA)
box(68, 2, 30, 17, "Diagnostics",
    "leakage audit, Exserohilum study,\ncalibration + temperature scaling,\nsteps-matched check", EVA)
for x in (17, 50, 83):
    arrow(x, 25, x, 19.6)
fig.savefig(OUT / "fig1_methodology.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------- Fig 2: dataset samples ----------------
classes = [("pyricularia", "PESGL_PYRISP_100.jpg", "Pyricularia (blast)\nn = 98"),
           ("smut", "PESGL_MOESBU_10.jpg", "Smut\nn = 75"),
           ("sclerospora", "PESGL_SCLPGR_10.jpg", "S. graminicola\n(downy mildew), n = 23"),
           ("healthy", "PESGL_12.jpg", "Healthy\nn = 23"),
           ("exserohilum", "PESGL_DRECRO_3.jpg", "E. rostratum\nn = 9")]
fig, axes = plt.subplots(1, 5, figsize=(10, 2.7), dpi=300)
for a, (c, f, t) in zip(axes, classes):
    im = ImageOps.fit(Image.open(ROOT / "Pearl_Millet_Dataset/Cache_512" / c / f).convert("RGB"), (400, 400))
    a.imshow(im); a.set_axis_off(); a.set_title(t, fontsize=8.5, color=INK)
fig.tight_layout()
fig.savefig(OUT / "fig2_samples.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------- Fig 3: leakage by protocol ----------------
df = pd.read_csv(ROOT / "Experiments/integrity/pearl_specimen_leakage_by_protocol.csv")
df = df[df.cosine_threshold.astype(str).str.match(r"^0\.\d+$")].copy()
df["thr"] = df.cosine_threshold.astype(float)
thr = sorted(df.thr.unique())
v1 = [df[(df.protocol == "fold") & (df.thr == t)].share.iloc[0] * 100 for t in thr]
sp = [df[(df.protocol == "fold_spec") & (df.thr == t)].share.iloc[0] * 100 for t in thr]
fig, ax = plt.subplots(figsize=(6, 3.4), dpi=300)
xs = range(len(thr)); w = 0.36
b1 = ax.bar([x - w / 2 - 0.01 for x in xs], v1, w, color=BLUE, label="Original folds (v1)")
b2 = ax.bar([x + w / 2 + 0.01 for x in xs], sp, w, color=ORANGE, label="Specimen-grouped folds")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{b.get_height():.0f}%",
                ha="center", fontsize=7.5, color=INK)
ax.set_xticks(list(xs)); ax.set_xticklabels([f"≥ {t:.2f}" for t in thr])
ax.set_xlabel("Cosine similarity to nearest same-class training image", color=INK)
ax.set_ylabel("Test images (%)", color=INK); ax.set_ylim(0, 92)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(MUTED); ax.spines["bottom"].set_color(MUTED)
ax.yaxis.grid(True, color="#e4e2da", lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "fig3_leakage.png", bbox_inches="tight", facecolor="white")
plt.close(fig)
print("done")
