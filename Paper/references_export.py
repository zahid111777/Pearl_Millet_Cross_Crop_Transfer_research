"""Write the reference outputs from references_db.R:

  references_verified.json    formatted entries for the numbered manuscript
  references_endnote.ris      EndNote import file (File > Import > File, import option "Reference Manager (RIS)")
  endnote_citation_keys.csv   key -> EndNote temporary-citation text, for checking matches after import
"""
import csv
import json
from urllib.parse import quote
from pathlib import Path
from references_db import R

HERE = Path(__file__).resolve().parent


def surname(a):
    return a.rstrip(",") if a.endswith(",") else a.split(",")[0].strip()


def initials_tight(a):
    if a.endswith(","):
        return a.rstrip(",")
    last, first = a.split(",", 1)
    return f"{last.strip()}, {first.strip().replace('. ', '.')}"


def link(r):
    if r.get("do") and not r.get("link_ur"):
        return "https://doi.org/" + quote(r["do"], safe="/:;().-_")
    return r.get("ur", "")


def pages(r, prefix=""):
    if r.get("sp") and r.get("ep"):
        return f"{prefix}{r['sp']}–{r['ep']}"
    return f"{prefix}{r['sp']}" if r.get("sp") else ""


def formatted(r):
    au = ", ".join(initials_tight(a) for a in r["au"]) + (", et al." if r.get("etal") else "")
    yr = f" ({r['py']})" if r.get("py") else ""
    ty = r["ty"]
    if ty == "JOUR":
        vol = r.get("vl", "") + (f"({r['is_']})" if r.get("is_") else "")
        loc = ", ".join(x for x in (vol, pages(r)) if x)
        body = f"{r['t2']}{(' ' + loc) if loc else ''}{yr}."
    elif ty == "CONF":
        bits = [f"In: {r['t2']}"] + ([pages(r, 'pp. ')] if r.get("sp") else []) + ([r["pb"]] if r.get("pb") else [])
        body = ", ".join(bits[:2]) + (f". {bits[2]}" if len(bits) > 2 else "") + f"{yr}."
    elif ty == "BOOK":
        body = f"{r['pb']}, {r['cy']}{yr}."
    elif ty == "RPRT":
        body = f"{r['t3']}. {r['pb']}, {r['cy']}{yr}."
    elif ty == "THES":
        body = f"{r['m3']}, {r['pb']}, {r['cy']}{yr}."
    elif ty == "ELEC":
        body = f"{r['pb']} (web page)."
    elif ty == "DATA":
        body = f"[Data set]. {r['pb']}{yr}." + (f" {r['note_text']}" if r.get("note_text") else "")
    elif ty == "COMP":
        body = f"[Software]. {r['pb']}{yr}."
    else:
        raise ValueError(ty)
    sep = " " if ty in ("DATA", "COMP") else ". "
    if sep == ". " and r["ti"].endswith("?"):
        sep = " "
    text = f"{au}: {r['ti']}{sep}{body}"
    if r.get("check"):
        text += " {{HL:[" + r["check"] + "]}}"
    return text


def ris(r):
    out = [f"TY  - {r['ty']}"]
    out += [f"AU  - {a}" for a in r["au"]]
    out.append(f"TI  - {r['ti']}")
    if r.get("t2"):
        out.append(f"T2  - {r['t2']}")
    if r.get("t3"):
        out.append(f"T3  - {r['t3']}")
    if r.get("py"):
        out.append(f"PY  - {r['py']}")
    for tag, k in (("VL", "vl"), ("IS", "is_"), ("SP", "sp"), ("EP", "ep"), ("PB", "pb"), ("CY", "cy"), ("M3", "m3")):
        if r.get(k):
            out.append(f"{tag}  - {r[k]}")
    if r.get("do"):
        out.append(f"DO  - {r['do']}")
    if link(r):
        out.append(f"UR  - {link(r)}")
    notes = [x for x in (r.get("note_text"), ("CHECK: " + r["check"]) if r.get("check") else None) if x]
    if r.get("etal"):
        notes.append("Author list incomplete in this record (et al.); complete it before formatting.")
    for n in notes:
        out.append(f"N1  - {n}")
    out.append(f"LB  - {r['key']}")
    out.append("ER  - ")
    return "\n".join(out)


def endnote_cite(r):
    return f"{surname(r['au'][0])}, {r['py']}" if r.get("py") else surname(r["au"][0])


if __name__ == "__main__":
    keys = [r["key"] for r in R]
    assert len(keys) == len(set(keys)), "duplicate keys"
    json.dump({r["key"]: {"text": formatted(r), "url": link(r), "endnote": endnote_cite(r)} for r in R},
              open(HERE / "references_verified.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (HERE / "references_endnote.ris").write_text("\n\n".join(ris(r) for r in R) + "\n", encoding="utf-8")
    with open(HERE / "endnote_citation_keys.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key", "endnote_temporary_citation", "first_author", "year", "title"])
        for r in R:
            w.writerow([r["key"], "{" + endnote_cite(r) + "}", surname(r["au"][0]), r.get("py", ""), r["ti"]])
    # ambiguity check: two records with the same surname + year would make an EndNote match ambiguous
    seen = {}
    for r in R:
        seen.setdefault(endnote_cite(r).lower(), []).append(r["key"])
    clash = {k: v for k, v in seen.items() if len(v) > 1}
    print(len(R), "references; ambiguous temporary citations:", clash or "none")
