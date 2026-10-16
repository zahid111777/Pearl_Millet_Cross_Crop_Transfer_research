"""Convert the code cells of a notebook into a plain script so long jobs can run headlessly.

usage: python nb_to_script.py Training_Notebook.ipynb out.py
Flags (RUN_*), SMOKE, FORCE_OVERWRITE are read from environment variables by the notebook itself.
"""
import json, sys

nb = json.load(open(sys.argv[1]))
out = ["import matplotlib; matplotlib.use('Agg')",
       "from IPython.display import display" ,
       ""]
for c in nb["cells"]:
    if c["cell_type"] != "code":
        continue
    lines = [l for l in "".join(c["source"]).splitlines() if not l.lstrip().startswith(("%", "!"))]
    out.append("\n".join(lines) + "\n")
open(sys.argv[2], "w").write("\n".join(out))
print("wrote", sys.argv[2])
