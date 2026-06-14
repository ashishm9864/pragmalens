from nlp_pipeline import run_pipeline


def main() -> None:
    sentence = "He finally stopped lying to investors."
    for item in run_pipeline(sentence, use_llm=False):
        print(f"{item.trigger_type}: {item.presupposition_str}")


if __name__ == "__main__":
    main()

