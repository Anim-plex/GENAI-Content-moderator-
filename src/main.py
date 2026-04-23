from __future__ import annotations

import argparse
import json
import sys

from moderator import ModerationConfig, moderate_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gen-AI content moderator")
    parser.add_argument("text", nargs="*", help="Text to moderate")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.text:
        text = " ".join(args.text)
    else:
        text = sys.stdin.read()

    config = ModerationConfig()
    result = moderate_text(text, config)

    if args.json:
        payload = {
            "score": result.score,
            "flags": result.flags,
            "reasons": result.reasons,
            "signals": result.signals,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Score: {result.score:.2f}")
        print("Flags:")
        for key, value in result.flags.items():
            print(f"  - {key}: {value}")
        print("Reasons:")
        for key, reasons in result.reasons.items():
            if reasons:
                print(f"  - {key}: {', '.join(reasons)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
