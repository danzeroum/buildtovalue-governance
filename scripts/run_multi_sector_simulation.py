#!/usr/bin/env python3
"""
BuildToValue - Multi-Sector Simulation Suite
Comprehensive validation across 6 high-risk sectors

Usage:
    python scripts/run_multi_sector_simulation.py
    python scripts/run_multi_sector_simulation.py --sectors healthcare,hr
    python scripts/run_multi_sector_simulation.py --quick  # 100 requests/sector
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import simulations
from simulations.healthcare_simulation import HealthcareSimulation
from simulations.hr_simulation import HRSimulation
from simulations.government_simulation import GovernmentSimulation
from simulations.infrastructure_simulation import InfrastructureSimulation
from simulations.education_simulation import EducationSimulation

AVAILABLE_SECTORS = {
    "healthcare": {
        "class": HealthcareSimulation,
        "name": "Healthcare",
        "icon": "🏥"
    },
    "hr": {
        "class": HRSimulation,
        "name": "HR & Employment",
        "icon": "👔"
    },
    "government": {
        "class": GovernmentSimulation,
        "name": "Government",
        "icon": "🏛️"
    },
    "infrastructure": {
        "class": InfrastructureSimulation,
        "name": "Critical Infrastructure",
        "icon": "⚡"
    },
    "education": {
        "class": EducationSimulation,
        "name": "Education",
        "icon": "🎓"
    }
}


def print_banner():
    print("\n" + "=" * 80)
    print("  🛡️  BuildToValue Framework v7.3")
    print("  Multi-Sector Compliance Simulation Suite")
    print("  EU AI Act High-Risk Scenarios Validation")
    print("=" * 80)
    print()


def run_sector_simulation(sector_key, requests, adversarial_ratio):
    """
    Runs simulation for a specific sector

    Args:
        sector_key: Key from AVAILABLE_SECTORS dict
        requests: Number of requests to simulate
        adversarial_ratio: Fraction of adversarial requests

    Returns:
        Dict with sector results
    """
    sector_info = AVAILABLE_SECTORS[sector_key]

    print(f"\n{sector_info['icon']} {sector_info['name'].upper()}")
    print("-" * 80)

    # Instantiate and run
    simulation = sector_info["class"](
        total_requests=requests,
        adversarial_ratio=adversarial_ratio
    )

    results = simulation.run()
    return results


def generate_comparative_report(all_results, output_path):
    """
    Generates comprehensive cross-sector comparison report

    Args:
        all_results: List of sector result dicts
        output_path: Path to save JSON report
    """
    print("\n" + "=" * 80)
    print("📊 CROSS-SECTOR COMPARATIVE ANALYSIS")
    print("=" * 80)
    print()

    # Summary table
    print(f"{'Sector':<25} {'Precision':<12} {'Recall':<12} {'Prevention':<12} {'Latency':<12}")
    print("-" * 80)

    for result in all_results:
        sector = result["sector"]
        metrics = result["metrics"]
        stats = result["statistics"]

        print(f"{sector:<25} "
              f"{metrics['precision']:<11.1%} "
              f"{metrics['recall']:<11.1%} "
              f"{metrics['prevention_rate']:<11.1f}% "
              f"{stats['avg_latency_ms']:<11.1f}ms")

    print()

    # Calculate aggregates
    avg_precision = sum(r["metrics"]["precision"] for r in all_results) / len(all_results)
    avg_recall = sum(r["metrics"]["recall"] for r in all_results) / len(all_results)
    avg_prevention = sum(r["metrics"]["prevention_rate"] for r in all_results) / len(all_results)
    avg_latency = sum(r["statistics"]["avg_latency_ms"] for r in all_results) / len(all_results)

    print(f"{'AVERAGE (All Sectors)':<25} "
          f"{avg_precision:<11.1%} "
          f"{avg_recall:<11.1%} "
          f"{avg_prevention:<11.1f}% "
          f"{avg_latency:<11.1f}ms")

    print()
    print("=" * 80)
    print()

    # Save JSON
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "7.3.0",
            "sectors_tested": len(all_results)
        },
        "aggregates": {
            "avg_precision": avg_precision,
            "avg_recall": avg_recall,
            "avg_prevention_rate": avg_prevention,
            "avg_latency_ms": avg_latency
        },
        "sector_results": all_results
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📄 Full report saved: {output_path}")
    print()


def main():
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

  # Custom configuration
  python scripts/run_multi_sector_simulation.py --requests 2000 --adversarial 0.4
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
        default=1000,
        help="Requests per sector (default: 1000)"
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
        help="Quick test mode (100 requests, 0.25 adversarial)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/multi_sector_results.json",
        help="Output JSON path (default: reports/multi_sector_results.json)"
    )

    args = parser.parse_args()

    # Quick mode overrides
    if args.quick:
        args.requests = 100
        args.adversarial = 0.25

    # Determine sectors to run
    if args.sectors == "all":
        sectors_to_run = list(AVAILABLE_SECTORS.keys())
    else:
        sectors_to_run = [s.strip() for s in args.sectors.split(",")]
        # Validate
        invalid = [s for s in sectors_to_run if s not in AVAILABLE_SECTORS]
        if invalid:
            print(f"❌ Error: Invalid sectors: {', '.join(invalid)}")
            print(f"Available: {', '.join(AVAILABLE_SECTORS.keys())}")
            sys.exit(1)

    # Banner
    print_banner()
    print(f"Configuration:")
    print(f"  Sectors:      {len(sectors_to_run)} ({', '.join(sectors_to_run)})")
    print(f"  Requests:     {args.requests} per sector")
    print(f"  Adversarial:  {args.adversarial * 100:.0f}%")
    print()

    # Run simulations
    all_results = []
    for sector_key in sectors_to_run:
        try:
            result = run_sector_simulation(sector_key, args.requests, args.adversarial)
            all_results.append(result)
        except Exception as e:
            print(f"❌ Error in {sector_key}: {e}")
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
