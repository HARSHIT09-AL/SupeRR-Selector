from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

THRESHOLDS = [30, 40, 50, 75, 100]

CONFIG = {
    "BATTERS": {
        "file": "batter_pressure_ratings.csv",
        "name": "striker_name",
        "score": "batting_pressure_score",
        "sample": "pressure_balls",
        "reliability_constant": 30
    },
    "BOWLERS": {
        "file": "bowler_pressure_ratings.csv",
        "name": "bowler_name",
        "score": "bowling_pressure_score",
        "sample": "pressure_legal_balls",
        "reliability_constant": 60
    }
}

report = []
report.append("=" * 72)
report.append("SUPERR SELECTOR - RESULT RELIABILITY CHECK")
report.append("=" * 72)
report.append("Purpose: evaluate sample support, score distribution and ranking stability.")
report.append("This is a diagnostic of the current ratings, not a prediction test.")
report.append("")

for role, cfg in CONFIG.items():
    path = DATA / cfg["file"]

    if not path.exists():
        raise FileNotFoundError(f"Missing rating file: {path}")

    df = pd.read_csv(path)
    name, score, sample = cfg["name"], cfg["score"], cfg["sample"]

    required = [name, score, sample]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"{cfg['file']} is missing required columns: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )

    df[score] = pd.to_numeric(df[score], errors="coerce")
    df[sample] = pd.to_numeric(df[sample], errors="coerce")
    df = df.dropna(subset=[name, score, sample]).copy()

    df["sample_reliability_factor"] = (
        df[sample] / (df[sample] + cfg["reliability_constant"])
    )
    df["rank_at_30_threshold"] = (
        df[score].rank(method="min", ascending=False).astype(int)
    )

    report.extend([
        "-" * 72,
        role,
        "-" * 72,
        f"Players in rating file: {len(df)}",
        f"Duplicate player names: {df[name].duplicated().sum()}",
        f"Missing scores: {df[score].isna().sum()}",
        f"Missing sample counts: {df[sample].isna().sum()}",
        f"Minimum sample: {df[sample].min():.0f}",
        f"Median sample: {df[sample].median():.1f}",
        f"Maximum sample: {df[sample].max():.0f}",
        f"Average score: {df[score].mean():.2f}",
        f"Median score: {df[score].median():.2f}",
        f"Score standard deviation: {df[score].std():.2f}",
        f"Lowest score: {df[score].min():.2f}",
        f"Highest score: {df[score].max():.2f}",
        f"Players scoring above 100: {(df[score] > 100).sum()}",
        f"Players scoring exactly 100: {(df[score] == 100).sum()}",
        f"Average sample reliability factor: {df['sample_reliability_factor'].mean():.3f}",
        ""
    ])

    # Qualification sensitivity and ranking stability
    baseline = df[df[sample] >= 30].copy()
    baseline_top = set(
        baseline.nlargest(10, score)[name].astype(str)
    )

    report.append("QUALIFICATION THRESHOLD SENSITIVITY")
    report.append("Threshold | Eligible | Top-10 overlap vs 30 | Spearman rank correlation")

    stability_rows = []

    for threshold in THRESHOLDS:
        qualified = df[df[sample] >= threshold].copy()
        top_names = set(
            qualified.nlargest(10, score)[name].astype(str)
        )

        overlap = len(baseline_top.intersection(top_names))

        common = baseline[[name, score]].merge(
            qualified[[name, score]],
            on=name,
            how="inner",
            suffixes=("_30", "_test")
        )

        if len(common) >= 2:
            rank_a = common[f'{score}_30'].rank(ascending=False)
            rank_b = common[f'{score}_test'].rank(ascending=False)
            a = rank_a.to_numpy(dtype=float)
            b = rank_b.to_numpy(dtype=float)
            if np.std(a) > 0 and np.std(b) > 0:
                correlation = float(np.corrcoef(a, b)[0, 1])
            else:
                correlation = np.nan
        else:
            correlation = np.nan

        stability_rows.append({
            "role": role,
            "minimum_sample": threshold,
            "eligible_players": len(qualified),
            "top10_overlap_vs_30": overlap,
            "common_players": len(common),
            "spearman_rank_correlation": correlation
        })

        corr_text = "N/A" if pd.isna(correlation) else f"{correlation:.3f}"
        report.append(
            f"{threshold:9} | {len(qualified):8} | "
            f"{overlap:20} | {corr_text}"
        )

    report.append("")
    report.append("TOP 10 PLAYERS AT ORIGINAL 30-SAMPLE THRESHOLD")

    top10 = baseline.nlargest(10, score)
    for i, (_, player) in enumerate(top10.iterrows(), start=1):
        report.append(
            f"{i:2}. {player[name]} | Score: {player[score]:.2f} | "
            f"Sample: {player[sample]:.0f} | "
            f"Reliability factor: {player['sample_reliability_factor']:.3f}"
        )

    report.append("")

    # Save player-level diagnostics
    detail = df.sort_values(score, ascending=False).copy()
    detail.to_csv(
        DATA / f"{role.lower()}_reliability_check.csv",
        index=False
    )

    pd.DataFrame(stability_rows).to_csv(
        DATA / f"{role.lower()}_ranking_stability.csv",
        index=False
    )

report.extend([
    "=" * 72,
    "INTERPRETATION GUIDE",
    "=" * 72,
    "1. Eligible players should decrease as the minimum sample rises.",
    "2. Top-10 overlap measures how many original leaders remain in the top 10.",
    "3. Spearman correlation measures ranking consistency among shared players.",
    "4. A higher sample reliability factor means a larger sample contribution.",
    "5. A score above 100 means performance exceeded its comparison baseline",
    "   after the model's reliability adjustment.",
    "",
    "IMPORTANT LIMITATION:",
    "This check does not establish future predictive accuracy, causal impact,",
    "or statistical confidence intervals. Those require additional validation.",
    "",
    "Generated files:",
    "reports/reliability_check_report.txt",
    "data/processed/batters_reliability_check.csv",
    "data/processed/bowlers_reliability_check.csv",
    "data/processed/batters_ranking_stability.csv",
    "data/processed/bowlers_ranking_stability.csv"
])

output = "\n".join(report)
(REPORTS / "reliability_check_report.txt").write_text(output, encoding="utf-8")
print(output)
print("\nReliability check files saved successfully.")

