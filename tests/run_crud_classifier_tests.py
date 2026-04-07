import sys
import csv

sys.path.insert(0, "src")

from api.pipeline.calendar import calendar

INPUT_CSV = "docs/tests/crud_classifier.csv"
OUTPUT_CSV = "docs/tests/crud_classifier_results.csv"


def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    results = []
    for row in rows:
        prompt = row["prompt"]
        expected = row["expected"]
        predicted = calendar(prompt)["operation"]
        passed = predicted == expected
        results.append(
            {
                "prompt": prompt,
                "expected": expected,
                "predicted": predicted,
                "pass": "PASS" if passed else "FAIL",
            }
        )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file, fieldnames=["prompt", "expected", "predicted", "pass"]
        )
        writer.writeheader()
        writer.writerows(results)


main()
