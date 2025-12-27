#!/usr/bin/env python3
"""Debug test for FAIRNESS category detection"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.governance.threat_classifier import (
    ThreatVectorClassifier,
    CATEGORY_PATTERNS,
    THREAT_PATTERNS
)
from src.domain.enums import ThreatCategory, ThreatDomain

# Test with simplified taxonomy
classifier = ThreatVectorClassifier(use_simplified=True)

issues = ["Discriminatory outcomes in loan approvals"]

print("="*70)
print("🔍 DEBUG: FAIRNESS Category Detection")
print("="*70)

# Check if keywords exist
fairness_config = CATEGORY_PATTERNS.get(ThreatCategory.FAIRNESS)
print(f"\n1️⃣ FAIRNESS Configuration:")
print(f"   Keywords: {fairness_config['keywords'][:10]}...")  # First 10
print(f"   'discriminatory' in keywords? {'discriminatory' in fairness_config['keywords']}")
print(f"   'discrimination' in keywords? {'discrimination' in fairness_config['keywords']}")

# Check text matching
text = " ".join(issues).lower()
print(f"\n2️⃣ Input Text:")
print(f"   Original: {issues[0]}")
print(f"   Lowercase: {text}")

# Manual keyword check
print(f"\n3️⃣ Manual Keyword Check:")
for kw in ["discrimination", "discriminatory", "loan"]:
    found = kw in text
    print(f"   '{kw}' in text? {found}")

# Run classifier
result = classifier.classify(issues)

print(f"\n4️⃣ Classification Result:")
print(f"   Detected categories: {result.detected_categories}")
print(f"   Detected domains: {result.detected_domains}")
print(f"   Matched keywords: {result.matched_keywords}")
print(f"   Confidence scores: {result.confidence_scores}")
print(f"   Weighted score: {result.weighted_score}")
print(f"   Primary threat: {result.primary_threat}")

print(f"\n5️⃣ Patterns Used:")
print(f"   Classifier using simplified? {classifier.use_simplified}")
print(f"   Number of patterns: {len(classifier.patterns)}")
print(f"   Pattern keys: {list(classifier.patterns.keys())}")

print("\n" + "="*70)

if ThreatCategory.FAIRNESS in result.detected_categories:
    print("✅ TEST PASSED: FAIRNESS detected")
else:
    print("❌ TEST FAILED: FAIRNESS not detected")
    print(f"\nExpected: {ThreatCategory.FAIRNESS}")
    print(f"Got: {result.detected_categories}")
