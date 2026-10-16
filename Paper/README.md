# Paper

Sources for the manuscript. All numbers come from the recorded result files in `../Experiments/` and
`../Experiments_vit_b16/`.

| File | Purpose |
|---|---|
| `build_tables.py` | regenerates `tables/*.md` (and a `02_results.md` draft) from the experiment CSVs |
| `02_results.template.md` | template used by `build_tables.py` |
| `tables/` | generated result tables, read by the manuscript builder |
| `make_figures.py` | draws `figures/fig1_methodology.png`, `fig2_samples.png` and `fig3_leakage.png` |
| `figures/` | Figures 1–3; the remaining figures are in `../Experiments*/figures/` |
| `references_db.py` | verified reference metadata (single source of truth) |
| `references_export.py` | writes `references_verified.json` plus an EndNote `.ris` file and citation-key list |
| `references_verified.json` | formatted references used by the manuscript builder |
| `docx_builder.py` | small python-docx helper (headings, tables, figures, equations, citations) |
| `build_paper_docx.py` | builds the Word manuscript; `--endnote` writes EndNote temporary citations |

Build order:

```bash
python Paper/build_tables.py
python Paper/references_export.py
python Paper/build_paper_docx.py              # numbered citations
python Paper/build_paper_docx.py --endnote    # {Author, Year} for EndNote: Update Citations and Bibliography
```
