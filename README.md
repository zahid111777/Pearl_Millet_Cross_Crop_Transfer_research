# Rice → Pearl-Millet Cross-Crop Transfer Learning

Code, recorded results and manuscript sources for the study *"Does intermediate rice-disease pre-training help
data-poor pearl-millet disease classification? A specimen-grouped evaluation with ConvNeXt and Vision Transformer
models"* (Zahid Rashid, Shawal Nasir).

## Summary

We test whether an intermediate training stage on rice-disease images (Paddy Doctor) improves five-class pearl-millet
disease classification (228 images after de-duplication) beyond ImageNet pre-training alone. We compare ImageNet,
ImageNet → rice and random → rice initialisation for **ConvNeXt-Tiny** and **ViT-B/16** at 10, 25, 50 and 100 % of
the target training data, with identical folds, subsets, seeds and training recipe (1,620 pearl-millet runs).

Main findings (specimen-grouped 5-fold cross-validation):

- **No measurable gain from rice pre-training over ImageNet** at any data fraction, in either architecture. Paired
  macro-F1 differences ranged from −0.011 to +0.008 (ConvNeXt) and from −0.031 to −0.016 (ViT), and all fold-level
  95 % confidence intervals included zero.
- **Rice-only pre-training transfers but does not replace ImageNet.** It improves on random initialisation by +0.27
  to +0.31 macro-F1 (ConvNeXt) but stays below ImageNet.
- **Repeated photographs of the same leaf leak across naive folds.** 42 % of test images had a near-identical
  training specimen. Specimen-grouped folds remove this and lower macro-F1 by 0.06–0.09.
- **Most remaining error is in *Exserohilum rostratum*** (9 images). Under-confidence is explained by label smoothing
  combined with class-weighted loss.

## Repository layout

```
Rice_Dataset/
  Helper/
    rice_dataset_audit.ipynb       rice data audit (integrity, exact and near duplicates, label conflicts)
    Training_Notebook.ipynb        full ConvNeXt-Tiny pipeline: manifests, rice pre-training, transfer grid,
                                   statistics, figures, diagnostic studies
    Training_Notebook_ViT.ipynb    the same pipeline for ViT-B/16 (writes to Experiments_vit_b16/)
    nb_to_script.py                converts a notebook into a script for headless runs
  Audit/                           rice audit outputs (CSV), used to build the rice manifest
Pearl_Millet_Dataset/
  Helper/pearl_millet_dataset_audit.ipynb   pearl-millet cleaning (MD5 and pHash de-duplication)
Experiments/                       ConvNeXt-Tiny results: manifests, per-run results and predictions, studies,
                                   tables, figures, integrity reports
Experiments_vit_b16/               ViT-B/16 results (same structure; data fractions in fractions/)

```

Datasets and model checkpoints are **not** included (see below).

## Data

| Dataset | Source | Put it in |
|---|---|---|
| Pearl millet, 5 classes (CC-BY-4.0) | ACRA (2025), Zenodo, https://doi.org/10.5281/zenodo.17086194 | `Pearl_Millet_Dataset/Raw/` (the 5 class zips), extracted to `Pearl_Millet_Dataset/Extracted/` |
| Paddy Doctor rice, 10 classes | Kaggle, https://www.kaggle.com/competitions/paddy-disease-classification/data | `Rice_Dataset/Raw/train_images.zip`, extracted to `Rice_Dataset/Extracted/` (`train.csv`, `train_images/`) |

The rice images are subject to the Kaggle competition rules and must not be redistributed. The audit notebooks
reproduce the cleaning steps, and `Rice_Dataset/Audit/` holds the resulting exclusion lists.

## Running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

1. Run the two audit notebooks (`Pearl_Millet_Dataset/Helper/`, `Rice_Dataset/Helper/rice_dataset_audit.ipynb`).
2. Open `Rice_Dataset/Helper/Training_Notebook.ipynb` and run it top to bottom. Every expensive step is behind a
   `RUN_*` flag in the last cell, all `False` by default. Flags can also be set as environment variables.
   - Run order: `RUN_STAGE1_RICE` and `RUN_STAGE1_RICE_SCRATCH` (rice pre-training), then `RUN_SPEC_FULL` and `RUN_SPEC_FRACTIONS` (specimen-grouped grid; `RUN_V1_*` for the original folds), then `RUN_CALIBRATION_STUDY`, `RUN_EXSEROHILUM_STUDY` and `RUN_STEPS_SENSITIVITY`, then `RUN_ANALYSIS` and `RUN_STUDY_ANALYSIS`.
   - Result files are append-only, finished runs are skipped, and existing checkpoints are never overwritten.
3. `Training_Notebook_ViT.ipynb` repeats the experiments for ViT-B/16 and compares them with the ConvNeXt results.
4. To run headlessly:

   ```bash
   python Rice_Dataset/Helper/nb_to_script.py Rice_Dataset/Helper/Training_Notebook.ipynb job.py
   RUN_STAGE1_RICE=1 python job.py
   ```

The notebooks use `~/cate_model/Pearl_millet_Prediction` as the project root by default. Set `PEARL_PROJECT_DIR` to
use another location. The stored manifests and prediction files identify images by the absolute path used when the
experiments were run, so a re-run in a different location regenerates the manifests rather than reusing them.

Original environment: Python 3.12, PyTorch 2.14 (CUDA 13.0), 2× NVIDIA RTX 5090. Runs are deterministic on that
hardware (a stored run was reproduced to 1e-16).

## Manuscript

`Paper/build_tables.py` regenerates the result tables from `Experiments*/`. `Paper/make_figures.py` draws Figures 1–3.
`Paper/references_export.py` writes the reference list (and an EndNote RIS file) from `Paper/references_db.py`.
`Paper/build_paper_docx.py` assembles the Word manuscript; it needs `python-docx`, and `--endnote` writes EndNote
temporary citations instead of numbers.
