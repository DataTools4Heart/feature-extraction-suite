"""
Randomly sample patients that have a MAGGIC or EHMRG score from each use case's already
extracted dataset, and write a Markdown report.

Reads directly from the onfhir-feast output written by the docker-compose stack in
`docker/docker-compose.yml` (bind-mounted to `<repo>/output-data`), under
`output-data/myFhirServer/dataset/<featureset-name>/<extraction-uuid>/`. No FHIR server or
running containers are required -- this only reads the Parquet/Delta files already on disk.

Score used per use case:
    - MAGGIC score (`maggic_total_score`): Study1 (UC1), Study4 (UC4), CARE-HEART Inpatient,
      CARE-HEART Outpatient, MAGGIC-MLP
    - EHMRG score (`ehmrg_score`): Study2 (UC2) -- this featureset does not compute a MAGGIC
      score at all, so EHMRG is used instead

If a use case's dataset has never been extracted (no directory under `dataset/`), it is
reported as "Not available". If a use case has more than one extraction (multiple UUID
subdirectories), the most recent one is used and the rest are ignored -- "most recent" is
taken from the `_feast_metadata` marker (the UUID feast currently considers active), falling
back to the newest Delta commit timestamp if that marker is missing or ambiguous.

Usage:
    python scripts/sample_score_cohorts.py --count 10 [--seed 42] [--output report.md]
"""

import argparse
import glob
import json
import os
import random
from datetime import datetime

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DATA_DIR = os.path.join(SCRIPT_DIR, "..", "output-data", "myFhirServer")
DEFAULT_REPORT_PATH = os.path.join(SCRIPT_DIR, "..", "score-cohort-sample.md")

# fs_dir is the *materialized* dataset directory name, i.e. each featureset JSON's "name"
# field (not its "id" -- for the two care-heart featuresets those differ: "id" is hyphenated,
# "name" is underscored, and "name" is what onfhir-feast actually uses as the output dir).
USE_CASES = [
    {"key": "UC1", "label": "Study1 (UC1)", "fs_dir": "study1-fs",
     "score_col": "maggic_total_score", "score_label": "MAGGIC score"},
    {"key": "UC2", "label": "Study2 (UC2)", "fs_dir": "study2-fs",
     "score_col": "ehmrg_score", "score_label": "EHMRG score"},
    {"key": "UC4", "label": "Study4 (UC4)", "fs_dir": "study4-fs",
     "score_col": "maggic_total_score", "score_label": "MAGGIC score"},
    {"key": "CARE-HEART-INPATIENT", "label": "CARE-HEART Inpatient", "fs_dir": "care_heart_inpatient_fs",
     "score_col": "maggic_total_score", "score_label": "MAGGIC score"},
    {"key": "CARE-HEART-OUTPATIENT", "label": "CARE-HEART Outpatient", "fs_dir": "care_heart_outpatient_fs",
     "score_col": "maggic_total_score", "score_label": "MAGGIC score"},
    {"key": "MAGGIC-MLP", "label": "MAGGIC-MLP", "fs_dir": "maggic-mlp-fs",
     "score_col": "maggic_total_score", "score_label": "MAGGIC score"},
]

# Non-extraction subdirectories that can appear alongside the UUID dataset dirs.
NON_EXTRACTION_DIRS = {"temp", "_feast_metadata"}


def find_latest_extraction(fs_path):
    """Return (uuid, uuid_dir_path, ignored_uuids) for a featureset's dataset dir.

    Returns (None, None, []) if the dataset was never extracted (dir missing or empty).
    """
    if not os.path.isdir(fs_path):
        return None, None, []

    candidates = sorted(
        d for d in os.listdir(fs_path)
        if d not in NON_EXTRACTION_DIRS and os.path.isdir(os.path.join(fs_path, d))
    )
    if not candidates:
        return None, None, []
    if len(candidates) == 1:
        return candidates[0], os.path.join(fs_path, candidates[0]), []

    active = _active_extraction_from_feast_metadata(fs_path, candidates)
    if active is None:
        active = max(candidates, key=lambda u: _latest_commit_timestamp(fs_path, u))

    ignored = [c for c in candidates if c != active]
    return active, os.path.join(fs_path, active), ignored


def _active_extraction_from_feast_metadata(fs_path, candidates):
    meta_dir = os.path.join(fs_path, "_feast_metadata")
    if not os.path.isdir(meta_dir):
        return None
    marked = [d for d in os.listdir(meta_dir) if os.path.isdir(os.path.join(meta_dir, d))]
    if len(marked) == 1 and marked[0] in candidates:
        return marked[0]
    return None


def _latest_commit_timestamp(fs_path, uuid):
    log_dir = os.path.join(fs_path, uuid, "_delta_log")
    latest = 0
    if not os.path.isdir(log_dir):
        return latest
    for fn in os.listdir(log_dir):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(log_dir, fn), encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    commit_info = entry.get("commitInfo")
                    if commit_info:
                        latest = max(latest, commit_info.get("timestamp", 0))
        except (OSError, json.JSONDecodeError):
            continue
    return latest


def load_scored_patients(uuid_dir, score_col):
    """Load pid/encounterId/eventTime/exitTime/<score_col> for rows with a non-null score."""
    part_files = sorted(glob.glob(os.path.join(uuid_dir, "part-*.snappy.parquet")))
    if not part_files:
        return None

    probe_columns = pd.read_parquet(part_files[0]).columns
    if score_col not in probe_columns:
        return None

    columns = ["pid", "eventTime", "exitTime", score_col]
    has_encounter = "encounterId" in probe_columns
    if has_encounter:
        columns.insert(1, "encounterId")

    df = pd.concat((pd.read_parquet(f, columns=columns) for f in part_files), ignore_index=True)
    if not has_encounter:
        df["encounterId"] = None

    return df[df[score_col].notna()].copy()


def one_row_per_patient(df):
    """Collapse to a single (deterministically chosen) row per unique patient."""
    return (
        df.sort_values(["pid", "encounterId"], na_position="last")
          .drop_duplicates(subset="pid", keep="first")
          .reset_index(drop=True)
    )


def fmt_timestamp(value):
    if value is None or pd.isna(value):
        return "—"
    return pd.Timestamp(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_results(output_data_dir, count, seed):
    rng = random.Random(seed)
    results = []

    for uc in USE_CASES:
        fs_path = os.path.join(output_data_dir, "dataset", uc["fs_dir"])
        uuid, uuid_dir, ignored = find_latest_extraction(fs_path)

        if uuid is None:
            results.append({**uc, "available": False})
            continue

        scored = load_scored_patients(uuid_dir, uc["score_col"])
        if scored is None:
            results.append({**uc, "available": False})
            continue

        deduped = one_row_per_patient(scored)
        total_patients = len(deduped)
        sample_n = min(count, total_patients)

        if sample_n > 0:
            chosen = sorted(rng.sample(range(total_patients), sample_n))
            selected = deduped.iloc[chosen].reset_index(drop=True)
        else:
            selected = deduped.iloc[0:0]

        results.append({
            **uc,
            "available": True,
            "uuid": uuid,
            "ignored": ignored,
            "total_patients": total_patients,
            "selected": selected,
        })

    return results


def build_report(results, count, seed):
    lines = [
        "# MAGGIC / EHMRG Score Cohort Sample",
        "",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
        "Source: `output-data/myFhirServer/dataset/` (onfhir-feast output, docker-compose stack)",
        f"Requested sample size per use case: **{count}**",
        f"Random seed: {seed if seed is not None else '(none — not reproducible across runs)'}",
        "",
        "## Summary",
        "",
        "| Use case | Score used | Extraction used | Total patients with score | Selected |",
        "|---|---|---|---|---|",
    ]

    for r in results:
        if not r["available"]:
            lines.append(f"| {r['label']} | {r['score_label']} | Not available | — | — |")
            continue
        extraction_note = r["uuid"]
        if r["ignored"]:
            extraction_note += f" ({len(r['ignored'])} older extraction(s) ignored)"
        lines.append(
            f"| {r['label']} | {r['score_label']} | `{extraction_note}` | "
            f"{r['total_patients']} | {len(r['selected'])} |"
        )

    lines += ["", "## Selected patients", ""]

    for r in results:
        lines.append(f"### {r['label']} — {r['score_label']}")
        lines.append("")
        if not r["available"]:
            lines.append(f"Not available — no dataset extraction found under `dataset/{r['fs_dir']}`.")
            lines.append("")
            continue
        if r["total_patients"] == 0:
            lines.append("No patients with this score were found in the extracted dataset.")
            lines.append("")
            continue

        lines.append("| Patient ID | Encounter ID | Eligibility Event Time | Eligibility Exit Time |")
        lines.append("|---|---|---|---|")
        for _, row in r["selected"].iterrows():
            encounter_id = row["encounterId"] if pd.notna(row["encounterId"]) else "N/A"
            lines.append(
                f"| {row['pid']} | {encounter_id} | "
                f"{fmt_timestamp(row['eventTime'])} | {fmt_timestamp(row['exitTime'])} |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Randomly sample patients with a MAGGIC/EHMRG score per use case and write a Markdown report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-n", "--count", type=int, required=True,
                         help="Number of patients to randomly select per use case")
    parser.add_argument("--seed", type=int, default=None,
                         help="Random seed, for a reproducible sample")
    parser.add_argument("--output-data-dir", default=DEFAULT_OUTPUT_DATA_DIR,
                         help="Path to output-data/myFhirServer (default: repo's output-data)")
    parser.add_argument("-o", "--output", default=DEFAULT_REPORT_PATH,
                         help="Path to write the Markdown report")
    args = parser.parse_args()

    results = collect_results(args.output_data_dir, args.count, args.seed)
    report = build_report(results, args.count, args.seed)

    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Wrote report to {output_path}")
    for r in results:
        if r["available"]:
            print(f"  {r['label']}: {r['total_patients']} total, {len(r['selected'])} selected "
                  f"(extraction {r['uuid']}{', others ignored' if r['ignored'] else ''})")
        else:
            print(f"  {r['label']}: not available")


if __name__ == "__main__":
    main()
