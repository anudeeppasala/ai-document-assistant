import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.rag_pipeline import generate_answer_from_chunks, retrieve_relevant_chunks


def _contains_keyword(answer: str, keywords: list[str]) -> float:
    lowered = answer.lower()
    hits = sum(1 for keyword in keywords if keyword.lower() in lowered)
    return hits / max(len(keywords), 1)


def _recall_at_k(matches: list[dict], expected_pages: list[int]) -> float:
    if not expected_pages:
        return 1.0
    retrieved = {int(match.get("page_number", -1)) for match in matches}
    hits = sum(1 for page in expected_pages if page in retrieved)
    return hits / len(expected_pages)


def run_eval(eval_path: Path) -> None:
    dataset = json.loads(eval_path.read_text(encoding="utf-8"))
    rows = []

    for case in dataset:
        question = case["question"]
        matches = retrieve_relevant_chunks(question)
        answer = generate_answer_from_chunks(question, matches)
        recall = _recall_at_k(matches, case.get("expected_page_numbers", []))
        answer_score = _contains_keyword(answer, case.get("expected_keywords", []))
        rows.append(
            {
                "id": case["id"],
                "question": question,
                "retrieval_recall_at_k": round(recall, 3),
                "answer_keyword_score": round(answer_score, 3),
                "match_count": len(matches),
            }
        )

    print(json.dumps(rows, indent=2))
    print(
        "\nAverages:",
        json.dumps(
            {
                "retrieval_recall_at_k": round(mean(row["retrieval_recall_at_k"] for row in rows), 3),
                "answer_keyword_score": round(mean(row["answer_keyword_score"] for row in rows), 3),
            },
            indent=2,
        ),
    )


if __name__ == "__main__":
    default_eval_path = ROOT / "eval" / "sample_eval_set.json"
    run_eval(default_eval_path)
