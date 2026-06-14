from examples import EXAMPLES
from nlp_pipeline import run_pipeline


def main() -> int:
    failures: list[str] = []
    total = 0
    for category, sentences in EXAMPLES.items():
        for sentence in sentences:
            total += 1
            items = run_pipeline(sentence, use_llm=False)
            print(f"{category}: {sentence} -> {len(items)}")
            for item in items:
                print(f"  - {item.trigger_type}: {item.presupposition_str}")
            if not items:
                failures.append(sentence)

    print(f"TOTAL={total} FAILURES={len(failures)}")
    for sentence in failures:
        print(f"NO_TRIGGER: {sentence}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

