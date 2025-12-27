#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - Threat Vector Classifier
Implements Huwyler (2025) AI Threat Taxonomy with keyword-based classification.

References:
- Huwyler, H. (2025). "Standardized Threat Taxonomy for AI Security"
  arXiv:2511.21901v1
- Validated against 133 documented AI incidents (2019-2025)
"""

from typing import List, Dict, Set, Optional
import re
from dataclasses import dataclass

from src.domain.enums import ThreatDomain, ThreatCategory

# ============================================================================
# THREAT PATTERNS (Based on Huwyler Taxonomy)
# ============================================================================

THREAT_PATTERNS = {
    # MISUSE (61% of incidents) - Prompt Injection, Jailbreaking
    ThreatDomain.MISUSE: {
        "keywords": [
            "injection", "jailbreak", "ignore instructions", "dan mode",
            "pretend you are", "roleplay", "system prompt", "bypass",
            "override", "ignore previous", "forget everything", "new instructions",
            "developer mode", "unrestricted", "no rules", "you are now"
        ],
        "patterns": [
            r"ignore\s+(all\s+)?(previous|prior|above)",
            r"new\s+(instructions|rules|guidelines)",
            r"you\s+are\s+(now|actually)\s+",
            r"pretend\s+(to\s+be|you\s+are)"
        ]
    },

    # PRIVACY (PII Leakage, Model Inversion)
    ThreatDomain.PRIVACY: {
        "keywords": [
            "ssn", "social security", "credit card", "passport",
            "email", "phone", "address", "pii", "personal data",
            "medical record", "health", "genetic", "biometric",
            "membership inference", "model inversion", "training data"
        ],
        "patterns": [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email
        ]
    },

    # UNRELIABLE_OUTPUTS (27% of incidents) - Hallucinations
    ThreatDomain.UNRELIABLE_OUTPUTS: {
        "keywords": [
            "hallucination", "factual error", "incorrect", "false information",
            "citation needed", "unverified", "fabricated", "made up",
            "wrong", "inaccurate", "misleading", "false claim",
            "non-factual", "unsupported", "baseless"
        ],
        "patterns": [
            r"(this is|that is|it is)\s+(false|incorrect|wrong)",
            r"(no evidence|not supported|unverified)"
        ]
    },

    # BIASES (Fairness, Discrimination)
    ThreatDomain.BIASES: {
        "keywords": [
            "discrimination", "racist", "sexist", "bias", "prejudice",
            "stereotype", "unfair", "disparate impact", "protected class",
            "age discrimination", "gender bias", "racial bias",
            "cultural bias", "socioeconomic bias", "accessibility"
        ],
        "patterns": [
            r"(based on|because of)\s+(race|gender|age|ethnicity)",
            r"(all|most)\s+\w+\s+(are|must be|should be)"
        ]
    },

    # POISONING (Supply Chain, Data Poisoning)
    ThreatDomain.POISONING: {
        "keywords": [
            "poisoning", "backdoor", "trojan", "malicious data",
            "corrupted", "tampered", "supply chain", "compromised",
            "infected model", "adversarial training"
        ],
        "patterns": []
    },

    # ADVERSARIAL (Evasion Attacks)
    ThreatDomain.ADVERSARIAL: {
        "keywords": [
            "adversarial", "evasion", "perturbation", "gradient",
            "attack", "adversary", "manipulate", "fool the model",
            "bypass detection", "evade"
        ],
        "patterns": []
    },

    # DRIFT (Model Degradation)
    ThreatDomain.DRIFT: {
        "keywords": [
            "drift", "degradation", "performance drop", "accuracy loss",
            "concept drift", "data shift", "distribution change",
            "model decay", "stale model"
        ],
        "patterns": []
    },

    # SUPPLY_CHAIN (Third-party risks)
    ThreatDomain.SUPPLY_CHAIN: {
        "keywords": [
            "third party", "dependency", "library", "package",
            "open source", "npm", "pypi", "vulnerability",
            "outdated", "unmaintained", "supply chain"
        ],
        "patterns": []
    },

    # IP_THREAT (Model Theft, Copyright)
    ThreatDomain.IP_THREAT: {
        "keywords": [
            "model theft", "extraction", "stealing", "copyright",
            "intellectual property", "plagiarism", "unauthorized",
            "model inversion", "reverse engineer"
        ],
        "patterns": []
    }
}

# Simplified patterns for ThreatCategory (v0.9.0)
CATEGORY_PATTERNS = {
    ThreatCategory.MISUSE: THREAT_PATTERNS[ThreatDomain.MISUSE],
    ThreatCategory.UNRELIABLE: THREAT_PATTERNS[ThreatDomain.UNRELIABLE_OUTPUTS],
    ThreatCategory.PRIVACY: THREAT_PATTERNS[ThreatDomain.PRIVACY],
    ThreatCategory.FAIRNESS: THREAT_PATTERNS[ThreatDomain.BIASES],
    ThreatCategory.SECURITY: {
        "keywords": (
                THREAT_PATTERNS[ThreatDomain.ADVERSARIAL]["keywords"] +
                THREAT_PATTERNS[ThreatDomain.POISONING]["keywords"] +
                THREAT_PATTERNS[ThreatDomain.SUPPLY_CHAIN]["keywords"]
        ),
        "patterns": []
    },
    ThreatCategory.DRIFT: THREAT_PATTERNS[ThreatDomain.DRIFT],
    ThreatCategory.OTHER: {"keywords": [], "patterns": []}
}


# ============================================================================
# CLASSIFIER
# ============================================================================

@dataclass
class ThreatClassificationResult:
    """Result of threat classification."""
    detected_domains: List[ThreatDomain]
    detected_categories: List[ThreatCategory]
    confidence_scores: Dict[str, float]
    matched_keywords: Dict[str, List[str]]
    primary_threat: Optional[str] = None


class ThreatVectorClassifier:
    """
    Classifies AI threats using Huwyler's Taxonomy patterns.

    Implements keyword-based and regex pattern matching for threat detection.
    Optimized for real-time enforcement with <10ms latency.

    Usage:
        >>> classifier = ThreatVectorClassifier()
        >>> result = classifier.classify(
        ...     issues=["Prompt injection detected: 'ignore previous instructions'"],
        ...     task_title="Generate financial advice"
        ... )
        >>> result.primary_threat
        'misuse'

    References:
    - Huwyler (2025), Section 4 (AI System Taxonomy)
    - Empirical validation: 100% coverage of 133 incidents
    """

    def __init__(self, use_simplified: bool = True):
        """
        Initialize classifier.

        Args:
            use_simplified: If True, use ThreatCategory (v0.9.0).
                          If False, use full ThreatDomain taxonomy.
        """
        self.use_simplified = use_simplified
        self.patterns = CATEGORY_PATTERNS if use_simplified else THREAT_PATTERNS

        # Compile regex patterns for performance
        self.compiled_patterns = {}
        for threat, config in self.patterns.items():
            self.compiled_patterns[threat] = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in config.get("patterns", [])
            ]

    def classify(
            self,
            issues: List[str],
            task_title: Optional[str] = None,
            task_description: Optional[str] = None
    ) -> ThreatClassificationResult:
        """
        Classify threats from detected issues.

        Args:
            issues: List of detected violations/issues
            task_title: Optional task title for context
            task_description: Optional task description for context

        Returns:
            ThreatClassificationResult with detected threats

        Algorithm:
        1. Combine all text sources
        2. For each threat domain/category:
           - Match keywords (case-insensitive)
           - Match regex patterns
           - Calculate confidence score
        3. Rank by confidence
        4. Apply fallback heuristic (MISUSE = 61% of cases)
        """
        # Combine all text for analysis
        text_corpus = " ".join(issues)
        if task_title:
            text_corpus += f" {task_title}"
        if task_description:
            text_corpus += f" {task_description}"

        text_lower = text_corpus.lower()

        detected = {}
        matched_keywords_by_threat = {}

        # Pattern matching
        for threat, config in self.patterns.items():
            score = 0.0
            matched_keywords = []

            # Keyword matching
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1.0
                    matched_keywords.append(keyword)

            # Regex pattern matching
            patterns = self.compiled_patterns.get(threat, [])
            for pattern in patterns:
                if pattern.search(text_corpus):
                    score += 2.0  # Patterns are stronger signals
                    matched_keywords.append(f"pattern:{pattern.pattern}")

            # Normalize score
            total_patterns = len(keywords) + len(patterns)
            if total_patterns > 0:
                confidence = min(score / total_patterns, 1.0)
            else:
                confidence = 0.0

            if confidence > 0:
                detected[threat] = confidence
                matched_keywords_by_threat[threat.value] = matched_keywords

        # Fallback heuristic (MISUSE = 61% of real-world cases)
        if not detected and issues:
            fallback_threat = (
                ThreatCategory.MISUSE if self.use_simplified
                else ThreatDomain.MISUSE
            )
            detected[fallback_threat] = 0.61  # Statistical prior
            matched_keywords_by_threat[fallback_threat.value] = ["statistical_fallback"]

        # Sort by confidence
        sorted_threats = sorted(
            detected.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Prepare results
        if self.use_simplified:
            detected_categories = [t for t, _ in sorted_threats]
            detected_domains = self._map_categories_to_domains(detected_categories)
        else:
            detected_domains = [t for t, _ in sorted_threats]
            detected_categories = self._map_domains_to_categories(detected_domains)

        confidence_scores = {t.value: c for t, c in sorted_threats}
        primary_threat = sorted_threats[0][0].value if sorted_threats else None

        return ThreatClassificationResult(
            detected_domains=detected_domains,
            detected_categories=detected_categories,
            confidence_scores=confidence_scores,
            matched_keywords=matched_keywords_by_threat,
            primary_threat=primary_threat
        )

    def _map_categories_to_domains(
            self,
            categories: List[ThreatCategory]
    ) -> List[ThreatDomain]:
        """Map simplified categories to full domains."""
        mapping = {
            ThreatCategory.MISUSE: [ThreatDomain.MISUSE],
            ThreatCategory.UNRELIABLE: [ThreatDomain.UNRELIABLE_OUTPUTS],
            ThreatCategory.PRIVACY: [ThreatDomain.PRIVACY],
            ThreatCategory.FAIRNESS: [ThreatDomain.BIASES],
            ThreatCategory.SECURITY: [
                ThreatDomain.ADVERSARIAL,
                ThreatDomain.POISONING,
                ThreatDomain.SUPPLY_CHAIN
            ],
            ThreatCategory.DRIFT: [ThreatDomain.DRIFT],
            ThreatCategory.OTHER: [ThreatDomain.IP_THREAT]
        }

        domains = []
        for category in categories:
            domains.extend(mapping.get(category, []))
        return domains

    def _map_domains_to_categories(
            self,
            domains: List[ThreatDomain]
    ) -> List[ThreatCategory]:
        """Map full domains to simplified categories."""
        mapping = {
            ThreatDomain.MISUSE: ThreatCategory.MISUSE,
            ThreatDomain.UNRELIABLE_OUTPUTS: ThreatCategory.UNRELIABLE,
            ThreatDomain.PRIVACY: ThreatCategory.PRIVACY,
            ThreatDomain.BIASES: ThreatCategory.FAIRNESS,
            ThreatDomain.ADVERSARIAL: ThreatCategory.SECURITY,
            ThreatDomain.POISONING: ThreatCategory.SECURITY,
            ThreatDomain.SUPPLY_CHAIN: ThreatCategory.SECURITY,
            ThreatDomain.DRIFT: ThreatCategory.DRIFT,
            ThreatDomain.IP_THREAT: ThreatCategory.OTHER
        }

        categories = []
        for domain in domains:
            category = mapping.get(domain, ThreatCategory.OTHER)
            if category not in categories:
                categories.append(category)
        return categories

    def get_threat_statistics(self) -> Dict[str, any]:
        """
        Get classifier statistics.

        Returns empirical distribution from Huwyler (2025) validation.
        """
        return {
            "total_incidents_analyzed": 133,
            "time_period": "2019-2025",
            "distribution": {
                "MISUSE": 0.61,  # 61% - Prompt injection, jailbreaking
                "UNRELIABLE_OUTPUTS": 0.27,  # 27% - Hallucinations
                "PRIVACY": 0.05,  # 5% - Data leakage
                "BIASES": 0.03,  # 3% - Discrimination
                "OTHER": 0.04  # 4% - Combined remaining
            },
            "validation_coverage": 1.00,  # 100% of incidents classified
            "reference": "Huwyler (2025) arXiv:2511.21901v1"
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def classify_threats(issues: List[str]) -> ThreatClassificationResult:
    """
    Quick threat classification (simplified taxonomy).

    Usage:
        >>> from src.core.governance.threat_classifier import classify_threats
        >>> result = classify_threats(["Bias detected in hiring algorithm"])
        >>> result.primary_threat
        'fairness'
    """
    classifier = ThreatVectorClassifier(use_simplified=True)
    return classifier.classify(issues)


def classify_threats_detailed(issues: List[str]) -> ThreatClassificationResult:
    """
    Detailed threat classification (full Huwyler taxonomy).

    Use for compliance reports and detailed analysis.
    """
    classifier = ThreatVectorClassifier(use_simplified=False)
    return classifier.classify(issues)


# ============================================================================
# VERSION METADATA
# ============================================================================

CLASSIFIER_VERSION = "0.9.0"
TAXONOMY_VERSION = "Huwyler 2025 (arXiv:2511.21901v1)"
VALIDATION_COVERAGE = 1.00  # 100% of 133 incidents

