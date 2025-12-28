#!/usr/bin/env python3

"""
Auditable Ledger Integrity Validator (HMAC Verification)

Usage:
    python scripts/validate_ledger.py logs/enforcement_ledger.jsonl
"""

import json
import hmac
import hashlib
import os
import sys
from pathlib import Path
from typing import Dict, List


def validate_ledger(ledger_path: Path, hmac_key: str) -> Dict:
    """
    Validates all HMAC signatures in the ledger

    Args:
        ledger_path: Path to ledger file
        hmac_key: HMAC key for validation

    Returns:
        Dict with validation statistics
    """
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")

    total_entries = 0
    valid_signatures = 0
    invalid_signatures = 0
    tampered_entries = []

    with open(ledger_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            total_entries += 1

            try:
                entry = json.loads(line.strip())

                # Check signature presence
                if "signature" not in entry:
                    invalid_signatures += 1
                    tampered_entries.append({
                        "line": line_num,
                        "reason": "Missing signature",
                        "entry_id": entry.get("system", "unknown"),
                        "timestamp": entry.get("timestamp", "unknown")
                    })
                    continue

                # Extract signature
                claimed_signature = entry.pop("signature")

                # Recalculate HMAC signature
                msg = json.dumps(entry, sort_keys=True).encode()
                expected_signature = hmac.new(
                    hmac_key.encode(),
                    msg,
                    hashlib.sha256
                ).hexdigest()

                # Compare (constant-time to prevent timing attacks)
                if hmac.compare_digest(claimed_signature, expected_signature):
                    valid_signatures += 1
                else:
                    invalid_signatures += 1
                    tampered_entries.append({
                        "line": line_num,
                        "reason": "Invalid signature (tampered ledger)",
                        "entry_id": entry.get("system", "unknown"),
                        "timestamp": entry.get("timestamp", "unknown"),
                        "claimed_sig": claimed_signature[:16] + "...",
                        "expected_sig": expected_signature[:16] + "..."
                    })

            except json.JSONDecodeError as e:
                invalid_signatures += 1
                tampered_entries.append({
                    "line": line_num,
                    "reason": f"Invalid JSON: {e}"
                })

    integrity_pct = (valid_signatures / total_entries * 100) if total_entries > 0 else 0

    return {
        "total_entries": total_entries,
        "valid_signatures": valid_signatures,
        "invalid_signatures": invalid_signatures,
        "tampered_entries": tampered_entries,
        "integrity_percentage": round(integrity_pct, 2)
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_ledger.py <ledger_file>")
        print("Example: python scripts/validate_ledger.py logs/enforcement_ledger.jsonl")
        sys.exit(1)

    ledger_path = Path(sys.argv[1])
    hmac_key = os.getenv("HMAC_KEY", "default-insecure-key")

    if hmac_key == "default-insecure-key":
        print("⚠️ WARNING: Using default HMAC key. Set HMAC_KEY environment variable!")
        print("")

    print(f"\n{'=' * 80}")
    print(f"🔍 BuildToValue - Ledger Integrity Validation")
    print(f"{'=' * 80}")
    print(f"File: {ledger_path}")
    print(f"{'=' * 80}\n")

    try:
        results = validate_ledger(ledger_path, hmac_key)

        print(f"📊 Validation Results:")
        print(f"{'─' * 80}")
        print(f"  Total entries: {results['total_entries']}")
        print(f"  Valid signatures: {results['valid_signatures']} ✅")
        print(f"  Invalid signatures: {results['invalid_signatures']} ❌")
        print(f"  Integrity: {results['integrity_percentage']}%")
        print(f"{'─' * 80}")

        if results['tampered_entries']:
            print(f"\n⚠️ SECURITY ALERT: {len(results['tampered_entries'])} tampered entry(ies) detected!")
            print(f"{'─' * 80}")

            for i, entry in enumerate(results['tampered_entries'][:10], 1):
                print(f"\n{i}. Line {entry['line']}:")
                print(f"   Reason: {entry['reason']}")
                if 'entry_id' in entry:
                    print(f"   System ID: {entry['entry_id']}")
                if 'timestamp' in entry:
                    print(f"   Timestamp: {entry['timestamp']}")
                if 'claimed_sig' in entry:
                    print(f"   Claimed: {entry['claimed_sig']}")
                    print(f"   Expected: {entry['expected_sig']}")

            if len(results['tampered_entries']) > 10:
                print(f"\n  ... and {len(results['tampered_entries']) - 10} more")

            print(f"\n{'─' * 80}")
            print(f"🚨 CRITICAL: Ledger integrity compromised!")
            print(f"  Action required: Investigate security breach (ISO 42001 Art. 12)")
            print(f"  Contact: security@buildtovalue.com")
            print(f"{'=' * 80}\n")
            sys.exit(1)

        else:
            print(f"\n✅ LEDGER INTEGRITY VERIFIED")
            print(f"  All {results['valid_signatures']} signatures are valid")
            print(f"  No tampering detected")
            print(f"{'=' * 80}\n")
            sys.exit(0)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
