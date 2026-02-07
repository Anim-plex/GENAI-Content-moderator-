# GENAI-Content-moderator-

A lightweight, offline Gen-AI content moderator that flags AI disclosure language,
spammy call-to-actions, toxic wording, sensitive data references, and repetition
patterns that often show up in low-quality AI-generated content.

## Features
- Pattern-based detection for AI disclosure, spam, toxicity, and sensitive data.
- Heuristic signals for repetition, unique word ratio, and duplicated sentences.
- Simple CLI with JSON output for easy integration.

## Quick start
```bash
python -m src.main "As an AI language model, click here to buy now"
```

### JSON output
```bash
python -m src.main --json "As an AI language model, click here to buy now"
```

## Library usage
```python
from src.moderator import moderate_text

result = moderate_text("As an AI language model, click here to buy now")
print(result.score)
print(result.flags)
```

## Notes
- This project is intentionally rule-based and runs offline.
- Tune thresholds by editing `ModerationConfig` in `src/moderator.py`.
