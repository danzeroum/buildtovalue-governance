# 🧪 Simulation Scripts

This folder contains **sector-specific simulation scripts** used to validate BuildToValue's governance engine.

## Available Simulations

| Sector | Script | Prevention Rate | Status |
|--------|--------|-----------------|--------|
| **Fintech** | `fintech_simulation.py` | 100% | ✅ Production |
| **Healthcare** | `healthcare_simulation.py` | 100% | ✅ Production |
| **HR & Employment** | `hr_simulation.py` | 100% | ✅ Production |
| **Critical Infrastructure** | `infrastructure_simulation.py` | 90% | ⚠️ Good |
| **Government Services** | `government_simulation.py` | 93.3% | ⚠️ Good |
| **Education** | `education_simulation.py` | 46.7% | ❌ Experimental |
| **Multi-Sector** | `multi_sector_simulation.py` | 86% avg | ✅ Benchmark |

## Running Simulations
Run individual sector
python examples/simulations/fintech_simulation.py

Run cross-sector analysis
python examples/simulations/multi_sector_simulation.py


## Simulation Architecture

All simulations extend `base_simulation.py` which provides:
- Threat generation (adversarial prompts)
- Confusion matrix calculation
- Financial impact estimation (EU AI Act penalties)
- HTML/JSON report generation

## Interpreting Results

### Metrics Explained

- **Prevention Rate**: % of threats successfully blocked (target: ≥95%)
- **Precision**: % of blocks that were actual threats (avoid false positives)
- **Recall**: % of threats caught (avoid false negatives)
- **F1-Score**: Harmonic mean of Precision and Recall

### Expected Performance

| Metric | Fintech | Healthcare | Education |
|--------|---------|------------|-----------|
| Precision | 100% | 78.9% | 100% |
| Recall | 100% | 100% | 46.7% |
| F1-Score | 100% | 88.2% | 63.6% |

**Note**: Education's low recall is a known issue (see EDUCATION_EXPERIMENTAL.md).

## Adding New Sectors

1. Create `new_sector_simulation.py` extending `BaseSimulation`
2. Define sector-specific threat patterns
3. Add safe patterns to `src/core/governance/sector_safe_patterns.py`
4. Run 100+ requests with 30% adversarial load
5. Document in this README

## References

- [Huwyler (2025) Threat Taxonomy](https://arxiv.org/abs/2511.21901)
- [EU AI Act Compliance Guide](../../docs/compliance/EU_AI_ACT_COMPLIANCE.md)
- [NIST AI RMF Mapping](../../docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)
