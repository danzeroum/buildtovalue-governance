#!/usr/bin/env python3
"""
BuildToValue v0.9.5.3 - Multi-Sector Simulation Suite (Gold Master)

Comprehensive validation across 5 high-risk sectors defined by EU AI Act Annex III.
Now compatible with v0.9.5.3 Gold Master architecture.

Features:
- Cross-sector comparative analysis
- Regulatory impact calculation (€/$ fines)
- Sub-threat breakdown by sector
- JSON/HTML export for audit compliance
- 100% Prevention Rate validation

Usage:
    # Run all sectors (default)
    python scripts/run_multi_sector_simulation.py

    # Run specific sectors
    python scripts/run_multi_sector_simulation.py --sectors healthcare,hr

    # Quick test (100 requests/sector)
    python scripts/run_multi_sector_simulation.py --quick

    # Custom configuration
    python scripts/run_multi_sector_simulation.py --requests 1000 --adversarial 0.4

Scientific Basis: Huwyler (2025) - arXiv:2511.21901v1 [cs.CR]
Compliance: EU AI Act, GDPR, NIST AI RMF 1.0, ISO/IEC 42001:2023
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Path setup
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import simulations
from simulations.healthcare_simulation import HealthcareSimulation
from simulations.hr_simulation import HRSimulation
from simulations.government_simulation import GovernmentSimulation
from simulations.infrastructure_simulation import InfrastructureSimulation
from simulations.education_simulation import EducationSimulation

# ============================================================================
# AVAILABLE SECTORS
# ============================================================================

AVAILABLE_SECTORS = {
    "healthcare": {
        "class": HealthcareSimulation,
        "name": "Healthcare",
        "icon": "🏥",
        "description": "Medical Diagnosis & Emergency Triage",
        "eu_ai_act": "Annex III(5)(a) - Health & Safety"
    },
    "hr": {
        "class": HRSimulation,
        "name": "HR & Employment",
        "icon": "👔",
        "description": "Automated Recruitment & Hiring",
        "eu_ai_act": "Annex III(4) - Employment Access"
    },
    "government": {
        "class": GovernmentSimulation,
        "name": "Government",
        "icon": "🏛️",
        "description": "Social Benefits & Fraud Detection",
        "eu_ai_act": "Annex III(5)(b) - Essential Public Services"
    },
    "infrastructure": {
        "class": InfrastructureSimulation,
        "name": "Critical Infrastructure",
        "icon": "⚡",
        "description": "Smart Grid Management",
        "eu_ai_act": "Annex III(2) - Critical Infrastructure"
    },
    "education": {
        "class": EducationSimulation,
        "name": "Education",
        "icon": "🎓",
        "description": "Automated Essay Grading",
        "eu_ai_act": "Annex III(3) - Education & Vocational Training"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print simulation suite banner."""
    print("\n" + "=" * 80)
    print(" 🛡️  BuildToValue Framework v0.9.5.3 (Gold Master)")
    print(" Multi-Sector Compliance Simulation Suite")
    print(" EU AI Act High-Risk Scenarios Validation")
    print("=" * 80)
    print()


def print_sector_summary():
    """Print available sectors summary."""
    print("📋 AVAILABLE SECTORS:")
    print()
    for key, info in AVAILABLE_SECTORS.items():
        print(f"  {info['icon']} {info['name']:<25} {info['description']}")
        print(f"     └─ {info['eu_ai_act']}")
    print()


def run_sector_simulation(
        sector_key: str,
        requests: int,
        adversarial_ratio: float,
        seed: int = None
) -> Dict:
    """
    Runs simulation for a specific sector.

    Args:
        sector_key: Key from AVAILABLE_SECTORS dict
        requests: Number of requests to simulate
        adversarial_ratio: Fraction of adversarial requests
        seed: Random seed for reproducibility

    Returns:
        Dict with sector results
    """
    sector_info = AVAILABLE_SECTORS[sector_key]

    print(f"\n{sector_info['icon']} {sector_info['name'].upper()}")
    print("-" * 80)
    print(f"Description: {sector_info['description']}")
    print(f"Regulation:  {sector_info['eu_ai_act']}")
    print()

    # Instantiate and run
    simulation = sector_info["class"](
        total_requests=requests,
        adversarial_ratio=adversarial_ratio,
        seed=seed
    )

    results = simulation.run()

    # Add sector metadata
    results["sector_key"] = sector_key
    results["sector_icon"] = sector_info["icon"]
    results["eu_ai_act_ref"] = sector_info["eu_ai_act"]

    return results


def generate_comparative_report(all_results: List[Dict], output_path: Path):
    """
    Generates comprehensive cross-sector comparison report.

    Args:
        all_results: List of sector result dicts
        output_path: Path to save JSON report
    """
    print("\n" + "=" * 80)
    print("📊 CROSS-SECTOR COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()

    # Summary table header
    print(f"{'Sector':<25} {'Prevention':<12} {'Precision':<12} {'F1-Score':<12} {'Latency':<12}")
    print("-" * 80)

    # Per-sector metrics
    for result in all_results:
        sector = result["sector"]
        metrics = result["metrics"]
        stats = result["statistics"]

        # Get icon
        sector_icon = result.get("sector_icon", "")

        print(f"{sector_icon} {sector:<22} "
              f"{metrics['prevention_rate']:<11.1f}% "
              f"{metrics['precision']:<11.1%} "
              f"{metrics['f1_score']:<11.1%} "
              f"{stats['avg_latency_ms']:<11.1f}ms")

    print()

    # Calculate aggregates
    avg_prevention = sum(r["metrics"]["prevention_rate"] for r in all_results) / len(all_results)
    avg_precision = sum(r["metrics"]["precision"] for r in all_results) / len(all_results)
    avg_recall = sum(r["metrics"]["recall"] for r in all_results) / len(all_results)
    avg_f1 = sum(r["metrics"]["f1_score"] for r in all_results) / len(all_results)
    avg_latency = sum(r["statistics"]["avg_latency_ms"] for r in all_results) / len(all_results)

    # Total fines prevented
    total_fines_eur = sum(r["statistics"]["TOTAL_FINES_PREVENTED_EUR"] for r in all_results)
    total_fines_usd = sum(r["statistics"]["TOTAL_FINES_PREVENTED_USD"] for r in all_results)

    # Aggregate confusion matrix
    total_tp = sum(r["statistics"]["TRUE_POSITIVES"] for r in all_results)
    total_fp = sum(r["statistics"]["FALSE_POSITIVES"] for r in all_results)
    total_tn = sum(r["statistics"]["TRUE_NEGATIVES"] for r in all_results)
    total_fn = sum(r["statistics"]["FALSE_NEGATIVES"] for r in all_results)

    print(f"{'📊 AVERAGE (All Sectors)':<25} "
          f"{avg_prevention:<11.1f}% "
          f"{avg_precision:<11.1%} "
          f"{avg_f1:<11.1%} "
          f"{avg_latency:<11.1f}ms")

    print()
    print("=" * 80)
    print()

    # Financial Impact
    print("💰 CONSOLIDATED FINANCIAL IMPACT:")
    print(f"   🇪🇺 Total EU Fines Prevented:  € {total_fines_eur:>15,}")
    print(f"   🇺🇸 Total US Fines Prevented:  $ {total_fines_usd:>15,}")
    print()

    # Confusion Matrix Summary
    print("📈 AGGREGATE CONFUSION MATRIX:")
    print(f"   True Positives:   {total_tp:>4} ✅")
    print(f"   False Positives:  {total_fp:>4} ⚠️")
    print(f"   True Negatives:   {total_tn:>4} ✅")
    print(f"   False Negatives:  {total_fn:>4} ❌")
    print()

    # Sub-threats breakdown
    print("🔍 TOP SUB-THREATS ACROSS SECTORS:")
    all_sub_threats = {}
    for result in all_results:
        for sub_threat, count in result.get("sub_threats", {}).items():
            if sub_threat not in all_sub_threats:
                all_sub_threats[sub_threat] = {"count": 0, "sectors": []}
            all_sub_threats[sub_threat]["count"] += count
            all_sub_threats[sub_threat]["sectors"].append(result["sector"])

    sorted_sub_threats = sorted(
        all_sub_threats.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )

    for i, (sub_threat, data) in enumerate(sorted_sub_threats[:10], 1):
        sectors_str = ", ".join(set(data["sectors"]))
        print(f"   {i:>2}. {sub_threat:<40} {data['count']:>3}x ({sectors_str})")

    print()
    print("=" * 80)
    print()

    # Success criteria
    success_criteria = {
        "prevention_rate": avg_prevention >= 95.0,
        "precision": avg_precision >= 0.95,
        "false_negatives": total_fn == 0,
        "false_positives": total_fp <= len(all_results) * 2  # Max 2 FP per sector
    }

    all_passed = all(success_criteria.values())

    if all_passed:
        print("✅ SUCCESS: All sectors meet Gold Master standards!")
        print("   └─ Prevention ≥95%, Precision ≥95%, FN=0, FP≤2/sector")
    else:
        print("⚠️  WARNING: Some metrics below target:")
        if not success_criteria["prevention_rate"]:
            print(f"   ❌ Prevention Rate: {avg_prevention:.1f}% (target: ≥95%)")
        if not success_criteria["precision"]:
            print(f"   ❌ Precision: {avg_precision:.1%} (target: ≥95%)")
        if not success_criteria["false_negatives"]:
            print(f"   ❌ False Negatives: {total_fn} (target: 0)")
        if not success_criteria["false_positives"]:
            print(f"   ⚠️  False Positives: {total_fp} (target: ≤{len(all_results) * 2})")

    print()

    # Save JSON report
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "0.9.5.3",
            "sectors_tested": len(all_results),
            "total_requests": sum(r["statistics"]["APPROVED"] + r["statistics"]["BLOCKED"] +
                                  r["statistics"]["CONDITIONAL"] + r["statistics"]["ESCALATE"]
                                  for r in all_results),
            "scientific_basis": "Huwyler (2025) - arXiv:2511.21901v1 [cs.CR]"
        },
        "aggregates": {
            "avg_prevention_rate": avg_prevention,
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_f1_score": avg_f1,
            "avg_latency_ms": avg_latency,
            "total_fines_prevented_eur": total_fines_eur,
            "total_fines_prevented_usd": total_fines_usd
        },
        "confusion_matrix": {
            "true_positives": total_tp,
            "false_positives": total_fp,
            "true_negatives": total_tn,
            "false_negatives": total_fn
        },
        "success_criteria": success_criteria,
        "all_passed": all_passed,
        "top_sub_threats": [
            {"name": st, "count": data["count"], "sectors": list(set(data["sectors"]))}
            for st, data in sorted_sub_threats[:10]
        ],
        "sector_results": all_results
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Full report saved: {output_path}")

    # Generate HTML report (optional)
    html_path = output_path.with_suffix('.html')
    generate_html_report(report, html_path)
    print(f"📄 HTML report saved: {html_path}")
    print()


def generate_html_report(data: Dict, output_path: Path):
    """Generate executive-ready HTML report."""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuildToValue v0.9.5.3 - Multi-Sector Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
               line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; 
               padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                       gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; 
                       box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 13px; color: #666; text-transform: uppercase; }}
        .success {{ color: #10b981; }}
        .warning {{ color: #f59e0b; }}
        .danger {{ color: #ef4444; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; 
                 font-size: 12px; font-weight: 600; }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ BuildToValue v0.9.5.3 - Multi-Sector Report</h1>
        <p><strong>Generated:</strong> {data['metadata']['timestamp']}</p>
        <p><strong>Sectors:</strong> {data['metadata']['sectors_tested']} | 
           <strong>Requests:</strong> {data['metadata']['total_requests']:,}</p>
    </div>

    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Avg Prevention Rate</div>
            <div class="metric-value {'success' if data['aggregates']['avg_prevention_rate'] >= 95 else 'warning'}">
                {data['aggregates']['avg_prevention_rate']:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Avg Precision</div>
            <div class="metric-value {'success' if data['aggregates']['avg_precision'] >= 0.95 else 'warning'}">
                {data['aggregates']['avg_precision']:.1%}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">False Negatives</div>
            <div class="metric-value {'success' if data['confusion_matrix']['false_negatives'] == 0 else 'danger'}">
                {data['confusion_matrix']['false_negatives']}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">EU Fines Prevented</div>
            <div class="metric-value">€{data['aggregates']['total_fines_prevented_eur']:,.0f}</div>
        </div>
    </div>

    <h2>📊 Sector Performance</h2>
    <table>
        <thead>
            <tr>
                <th>Sector</th>
                <th>Prevention</th>
                <th>Precision</th>
                <th>F1-Score</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{r['sector_icon']} {r['sector']}</td>
                <td>{r['metrics']['prevention_rate']:.1f}%</td>
                <td>{r['metrics']['precision']:.1%}</td>
                <td>{r['metrics']['f1_score']:.1%}</td>
                <td><span class="badge badge-{'success' if r['metrics']['prevention_rate'] >= 95 else 'warning'}">
                    {'PASS' if r['metrics']['prevention_rate'] >= 95 else 'WARN'}
                </span></td>
            </tr>
            ''' for r in data['sector_results'])}
        </tbody>
    </table>

    <h2>🔍 Top Sub-Threats</h2>
    <table>
        <thead>
            <tr><th>Rank</th><th>Sub-Threat</th><th>Count</th><th>Sectors</th></tr>
        </thead>
        <tbody>
            {''.join(f'''
            <tr>
                <td>{i}</td>
                <td>{st['name']}</td>
                <td>{st['count']}</td>
                <td>{', '.join(st['sectors'])}</td>
            </tr>
            ''' for i, st in enumerate(data['top_sub_threats'], 1))}
        </tbody>
    </table>

    <div style="margin-top: 40px; padding: 20px; background: {'#d1fae5' if data['all_passed'] else '#fef3c7'}; 
                border-radius: 8px; text-align: center;">
        <h3>{'✅ All Sectors PASSED' if data['all_passed'] else '⚠️ Some Metrics Below Target'}</h3>
        <p>Scientific Basis: {data['metadata']['scientific_basis']}</p>
    </div>
</body>
</html>
"""

    output_path.write_text(html, encoding='utf-8')


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution function."""

    parser = argparse.ArgumentParser(
        description="BuildToValue Multi-Sector Simulation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available Sectors:
  {', '.join(AVAILABLE_SECTORS.keys())}

Examples:
  # Run all sectors (default)
  python scripts/run_multi_sector_simulation.py

  # Run specific sectors
  python scripts/run_multi_sector_simulation.py --sectors healthcare,hr

  # Quick test (100 requests per sector)
  python scripts/run_multi_sector_simulation.py --quick

  # Custom configuration with seed
  python scripts/run_multi_sector_simulation.py --requests 2000 --adversarial 0.4 --seed 42
        """
    )

    parser.add_argument(
        "--sectors",
        type=str,
        default="all",
        help="Comma-separated list of sectors (default: all)"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Requests per sector (default: 100)"
    )

    parser.add_argument(
        "--adversarial",
        type=float,
        default=0.30,
        help="Adversarial ratio (default: 0.30)"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test mode (100 requests, 0.30 adversarial)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="reports/multi_sector_results.json",
        help="Output JSON path (default: reports/multi_sector_results.json)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available sectors and exit"
    )

    args = parser.parse_args()

    # List sectors and exit
    if args.list:
        print_banner()
        print_sector_summary()
        return

    # Quick mode overrides
    if args.quick:
        args.requests = 100
        args.adversarial = 0.30

    # Determine sectors to run
    if args.sectors == "all":
        sectors_to_run = list(AVAILABLE_SECTORS.keys())
    else:
        sectors_to_run = [s.strip() for s in args.sectors.split(",")]

    # Validate sectors
    invalid = [s for s in sectors_to_run if s not in AVAILABLE_SECTORS]
    if invalid:
        print(f"❌ Error: Invalid sectors: {', '.join(invalid)}")
        print(f"Available: {', '.join(AVAILABLE_SECTORS.keys())}")
        print("\nUse --list to see all available sectors")
        sys.exit(1)

    # Banner
    print_banner()
    print(f"Configuration:")
    print(f"  Sectors:      {len(sectors_to_run)} ({', '.join(sectors_to_run)})")
    print(f"  Requests:     {args.requests} per sector")
    print(f"  Adversarial:  {args.adversarial * 100:.0f}%")
    print(f"  Seed:         {args.seed}")
    print()

    # Run simulations
    all_results = []
    for sector_key in sectors_to_run:
        try:
            result = run_sector_simulation(
                sector_key,
                args.requests,
                args.adversarial,
                args.seed
            )
            all_results.append(result)
        except Exception as e:
            print(f"❌ Error in {sector_key}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Generate report
    if all_results:
        generate_comparative_report(all_results, Path(args.output))
        print("✅ Multi-sector simulation completed successfully!")
    else:
        print("❌ No simulations completed")
        sys.exit(1)


if __name__ == "__main__":
    main()
