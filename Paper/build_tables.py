"""Generate every table in the Results section directly from the recorded CSV files (no hand-typed numbers).
usage: python build_tables.py   (reads Experiments/ and Experiments_vit_b16/, writes Paper/tables/*.md and Paper/02_results.md from 02_results.template.md)"""
import pandas as pd, numpy as np, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent; C = R / "Experiments"; V = R / "Experiments_vit_b16"; OUT = Path(__file__).resolve().parent / "tables"
ARCH = ["ConvNeXt-Tiny", "ViT-B/16"]; EXPS = ["imagenet_full", "rice_full", "ricescratch_full"]; FR = [0.1, 0.25, 0.5, 1.0]
LAB = {"imagenet_full": "ImageNet", "rice_full": "ImageNet → rice", "ricescratch_full": "random → rice", "scratch_full": "random"}
CLS = ["exserohilum", "healthy", "pyricularia", "sclerospora", "smut"]
def md(df, align=None):
    cols = list(df.columns); s = "| " + " | ".join(cols) + " |\n|" + "|".join(["---"] * len(cols)) + "|\n"
    for _, r in df.iterrows(): s += "| " + " | ".join(str(x) for x in r.values) + " |\n"
    return s
def pm(m, sd, d=3): return f"{m:.{d}f} ± {sd:.{d}f}"
def verdict(c):
    if isinstance(c, str) and c.startswith("supported"):
        a, b = re.findall(r"supported: (\S+) ([<>]) (\S+)", c)[0][0], None
        return c.replace("supported: ", "supported (").replace("ConvNeXt-Tiny:", "ConvNeXt ").replace("ViT-B/16:", "ViT ").replace("_full", "") + ")"
    return "inconclusive"
T = {}
# ---- T2 rice pre-training
rows = []
for arch, base in (("ConvNeXt-Tiny", C), ("ViT-B/16", V)):
    for nm, lab in (("rice", "ImageNet → rice (15 ep)"), ("rice_scratch", "random → rice (≤100 ep)")):
        d = pd.read_csv(base / "tables" / f"rice_test_summary_{nm}.csv").iloc[0]
        rows.append({"Architecture": arch, "Pre-training": lab, "Test acc.": f"{d.acc:.3f}", "Balanced acc.": f"{d.bal_acc:.3f}", "Macro-F1": f"{d.macro_f1:.3f}", "ECE": f"{d.ece:.3f}"})
T["T2"] = md(pd.DataFrame(rows))
# ---- T1 leakage
L = pd.read_csv(C / "integrity" / "pearl_specimen_leakage_by_protocol.csv"); L = L[L.cosine_threshold.astype(str).isin(["0.9", "0.93", "0.95", "0.97"])]
rows = []
for thr in ["0.9", "0.93", "0.95", "0.97"]:
    a = L[(L.protocol == "fold") & (L.cosine_threshold.astype(str) == thr)].iloc[0]; b = L[(L.protocol == "fold_spec") & (L.cosine_threshold.astype(str) == thr)].iloc[0]
    rows.append({"Cosine similarity ≥": thr, "Original folds (v1)": f"{int(a.test_images_with_near_specimen_in_train)} / 228 ({a.share:.0%})", "Specimen-grouped folds": f"{int(b.test_images_with_near_specimen_in_train)} / 228 ({b.share:.0%})"})
T["T1"] = md(pd.DataFrame(rows))
# ---- T3 main results: macro-F1, balanced accuracy, accuracy
S = pd.read_csv(V / "tables" / "fractions_summary.csv")
for key, met, name in (("T3a", "macro_f1_present", "Macro-F1"), ("T3b", "bal_acc", "Balanced accuracy"), ("T3c", "acc", "Accuracy")):
    rows = []
    for arch in ARCH:
        for e in EXPS:
            g = S[(S.arch == arch) & (S.exp == e)].set_index("frac"); rows.append({"Architecture": arch, "Initialisation": LAB[e], **{f"{int(f*100)} %": pm(g.loc[f, met + "_mean"], g.loc[f, met + "_sd_folds"]) for f in FR}})
    T[key] = md(pd.DataFrame(rows))
# ---- T4 rice vs ImageNet, T5 ViT vs ConvNeXt (+ secondary)
P = pd.read_csv(V / "tables" / "fractions_paired_stats.csv")
def paired_md(sub, label_col):
    rows = []
    for _, r in sub.iterrows():
        rows.append({label_col[0]: label_col[1](r), "Data": f"{int(r.frac*100)} %", "Δ macro-F1 (fold mean)": f"{r.fold_mean_diff:+.3f}", "d_z": f"{r.cohens_dz:+.2f}", "95 % t-CI (folds)": f"[{r.t_ci_lo:+.3f}, {r.t_ci_hi:+.3f}]",
                     "Folds won": f"{int(r.folds_a_wins)}/5", "Pooled Δ [bootstrap 95 % CI]": f"{r.pooled_diff:+.3f} [{r.boot_lo:+.3f}, {r.boot_hi:+.3f}]", "Holm p (bootstrap)": f"{r.boot_p_holm:.3f}", "Δ bal. acc.": (f"{r.bal_acc_fold_mean_diff:+.3f}" if "bal_acc_fold_mean_diff" in r.index and pd.notna(r.bal_acc_fold_mean_diff) else "–"), "Verdict": verdict(r.claim)})
    return md(pd.DataFrame(rows))
T["T4"] = paired_md(P[P.family.str.startswith("rice_vs_imagenet|")], ("Architecture", lambda r: r.family.split("|")[1]))
T["T5"] = paired_md(P[P.family.str.startswith("vit_vs_convnext|")], ("Initialisation", lambda r: LAB[r.family.split("|")[1]]))
T["T5b"] = paired_md(P[P.family.str.startswith(("ricescratch_vs_imagenet", "rice_vs_ricescratch"))], ("Comparison", lambda r: f"{r.family.split('|')[1]}: " + ("random→rice vs ImageNet" if r.family.startswith("ricescratch") else "ImageNet→rice vs random→rice")))
# ConvNeXt only: rice-only vs random
cp = pd.read_csv(C / "tables" / "paired_stats_spec.csv"); cs = cp[(cp.a == "ricescratch_full") & (cp.b == "scratch_full")]
T["T5c"] = paired_md(cs, ("Comparison", lambda r: "ConvNeXt: random→rice vs random"))
# ---- T6 per-class pooled F1 (100 % and 10 %)
pc = pd.read_csv(V / "tables" / "fractions_per_class_pooled.csv"); pc["arch"] = pc.exp.str.split("|").str[0]; pc["e"] = pc.exp.str.split("|").str[1]
for key, fr in (("T6a", 1.0), ("T6b", 0.1)):
    rows = []
    for arch in ARCH:
        for e in EXPS:
            g = pc[(pc.arch == arch) & (pc.e == e) & np.isclose(pc.frac, fr)].set_index("cls"); rows.append({"Architecture": arch, "Initialisation": LAB[e], **{c: f"{g.loc[c,'f1']:.3f}" for c in CLS}})
    T[key] = md(pd.DataFrame(rows))
ex = pc[pc.cls == "exserohilum"]; rows = []
for arch in ARCH:
    for e in EXPS:
        g = ex[(ex.arch == arch) & (ex.e == e)].set_index("frac"); rows.append({"Architecture": arch, "Initialisation": LAB[e], **{f"{int(f*100)} %": f"P {g.loc[f,'precision']:.2f} / R {g.loc[f,'recall']:.2f} / F1 {g.loc[f,'f1']:.2f}" for f in FR}})
T["T6c"] = md(pd.DataFrame(rows))
# ---- T7 calibration
cal = pd.read_csv(V / "tables" / "fractions_vit_calibration_pooled.csv"); rows = []
for e in EXPS:
    for f in FR:
        g = cal[(cal.exp == e) & np.isclose(cal.frac, f)].iloc[0]; rows.append({"ViT-B/16 initialisation": LAB[e], "Data": f"{int(f*100)} %", "Accuracy": f"{g.acc_mean:.3f}", "Mean confidence": f"{g.mean_conf_mean:.3f}", "ECE (15 bins)": f"{g.ece15_mean:.3f} ± {g.ece15_std:.3f}", "NLL": f"{g.nll_mean:.3f}", "Brier": f"{g.brier_mean:.3f}"})
T["T7a"] = md(pd.DataFrame(rows))
cc = pd.read_csv(C / "tables" / "calibration_summary.csv"); rows = []
for v in ["base", "ls0", "nobal", "ls0_nobal", "ep80"]:
    for init in ["imagenet", "rice"]:
        a = cc[(cc.variant == v) & (cc.init == init) & (cc.calibration == "raw")].iloc[0]; b = cc[(cc.variant == v) & (cc.init == init) & (cc.calibration == "temp_scaled")].iloc[0]
        rows.append({"Variant": {"base": "base (label smoothing 0.1, class weights)", "ls0": "no label smoothing", "nobal": "no class weights", "ls0_nobal": "neither", "ep80": "80 epochs"}[v], "Init": "ImageNet" if init == "imagenet" else "ImageNet → rice",
                     "Acc.": f"{a.acc_mean:.3f}", "Mean conf.": f"{a.mean_conf_mean:.3f}", "ECE raw": f"{a.ece15_mean:.3f} ± {a.ece15_std:.3f}", "ECE after temp. scaling": f"{b.ece15_mean:.3f} ± {b.ece15_std:.3f}", "NLL raw": f"{a.nll_mean:.3f}"})
T["T7b"] = md(pd.DataFrame(rows))
# ---- T8 protocol effect (ConvNeXt, 100 %)
s1 = pd.read_csv(C / "tables" / "summary_v1.csv"); s2 = pd.read_csv(C / "tables" / "summary_spec.csv"); rows = []
for e in ["scratch_full", "ricescratch_full", "imagenet_full", "rice_full"]:
    a = s1[(s1.exp == e) & np.isclose(s1.frac, 1.0)].iloc[0]; b = s2[(s2.exp == e) & np.isclose(s2.frac, 1.0)].iloc[0]
    rows.append({"Initialisation (ConvNeXt, full fine-tune, 100 %)": LAB[e], "Original folds": f"{a.macro_f1:.3f}", "Specimen-grouped folds": f"{b.macro_f1:.3f}", "Difference": f"{b.macro_f1 - a.macro_f1:+.3f}"})
T["T8"] = md(pd.DataFrame(rows))
# ---- T9 steps-matched sensitivity
st = pd.read_csv(C / "tables" / "steps_sensitivity_spec.csv"); rows = []
for _, r in st.iterrows(): rows.append({"Epochs": r.epochs, "Policy": r.policy, "Data": f"{int(r.frac*100)} %", "ImageNet": f"{r.imagenet:.3f}", "ImageNet → rice": f"{r.rice:.3f}", "Δ (rice − ImageNet) [95 % t-CI]": f"{r.diff_rice_minus_imagenet:+.3f} [{r.t_ci_lo:+.3f}, {r.t_ci_hi:+.3f}]", "Folds rice wins": f"{int(r.folds_rice_wins)}/5"})
T["T9"] = md(pd.DataFrame(rows))
# ---- T10 ConvNeXt transfer policies (rice vs ImageNet)
pr = cp[(cp.family == "primary") & (cp.a != "rice_full")]; rows = []
for _, r in pr.iterrows(): rows.append({"Policy": r.a.replace("rice_", ""), "Data": f"{int(r.frac*100)} %", "Δ macro-F1 (fold mean)": f"{r.fold_mean_diff:+.3f}", "95 % t-CI": f"[{r.t_ci_lo:+.3f}, {r.t_ci_hi:+.3f}]", "Folds rice wins": f"{int(r.folds_a_wins)}/5", "Pooled Δ [bootstrap 95 % CI]": f"{r.pooled_diff:+.3f} [{r.boot_lo:+.3f}, {r.boot_hi:+.3f}]", "Verdict": verdict(r.claim)})
T["T10"] = md(pd.DataFrame(rows))
# ---- T11 Exserohilum study
es = pd.read_csv(C / "tables" / "exserohilum_study_summary.csv"); rows = []
for _, r in es.sort_values(["init", "variant"]).iterrows(): rows.append({"Init": "ImageNet" if r.init == "imagenet" else "ImageNet → rice", "Variant": {"base": "base", "sampler": "class-balanced sampler", "nobal": "no class weights", "ls0": "no label smoothing", "res384": "384 px"}[r.variant], "Exserohilum precision": f"{r.exs_precision:.2f}", "recall": f"{r.exs_recall:.2f}", "F1": f"{r.exs_f1:.2f}", "Pyricularia→Exserohilum": f"{r.pyr_to_exs:.2f}", "Macro-F1 (pooled)": f"{r.macro_f1_pooled:.3f}"})
T["T11"] = md(pd.DataFrame(rows))
di = pd.read_csv(C / "tables" / "exserohilum_image_diagnostics.csv"); rows = []
for _, r in di.iterrows(): rows.append({"Image": r.image.replace("PESGL_", "").replace(".jpg", ""), "Correct (spec. folds, all runs)": f"{r.spec_correct_rate:.0%}", "Nearest same-class cosine": f"{r.nearest_same_class_cos:.2f}", "Nearest other-class cosine": f"{r.nearest_other_class_cos:.2f}", "Nearest other class": r.nearest_other_class_is})
T["T12"] = md(pd.DataFrame(rows))
# ---- write
for k, v in T.items(): (OUT / f"{k}.md").write_text(v)
tpl = (Path(__file__).resolve().parent / "02_results.template.md").read_text()
out = re.sub(r"\{\{(T\w+)\}\}", lambda m: T[m.group(1)], tpl)
(Path(__file__).resolve().parent / "02_results.md").write_text(out); print("tables:", ", ".join(T), "| wrote 02_results.md")
