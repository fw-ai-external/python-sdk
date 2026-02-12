"""
Dataset Loading and Evaluation Utilities.

Functions for loading GSM8K-style math datasets and evaluating model responses.

GSM8K dataset format (JSONL, one example per line):
    {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
     "ground_truth": {"response": "42", "explanation": "..."}}

The evaluation function extracts the numeric answer from model responses and
compares against the ground truth. It supports several response formats:
- JSON: {"response": "42"}
- XML: <answer>42</answer>
- Plain number at end of text

Copyright (c) Fireworks AI, Inc. and affiliates.
"""

from __future__ import annotations

import re
import json
from typing import Any, Dict, List, Tuple, Optional

import httpx

from . import log


def extract_answer_digits(text: str) -> Optional[str]:
    """Extract the numeric answer from a model response or ground truth.

    Tries multiple formats in order:
    1. JSON: {"response": "42"} or {"explanation": "...", "response": "42"}
    2. XML: <answer>42</answer>
    3. Fallback: last number in the text

    Returns:
        The extracted number as a string, or None if no number found
    """
    # Try JSON format first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "response" in parsed:
            digits = re.search(r"(-?\d+)", str(parsed["response"]))
            return digits.group(1) if digits else None
    except (json.JSONDecodeError, TypeError):
        pass

    # Try XML format: <answer>42</answer>
    match = re.search(r"<answer>(.*?)</answer>", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        digits = re.search(r"(-?\d+)", match.group(1))
        return digits.group(1) if digits else None

    # Fallback: last number in the text
    digits = re.search(r"(-?\d+)\s*$", text.strip())
    return digits.group(1) if digits else None


def evaluate_gsm8k_response(response: str, ground_truth: str) -> Tuple[float, str]:
    """Evaluate a model response against the ground truth answer.

    Returns:
        (reward, explanation) where reward is 1.0 for correct, 0.0 for incorrect
    """
    predicted = extract_answer_digits(response)
    truth = extract_answer_digits(str(ground_truth))
    if predicted is None or truth is None:
        return 0.0, f"Missing answer. Predicted: {predicted}, Truth: {truth}"
    if predicted == truth:
        return 1.0, f"Correct! Predicted: {predicted}, Truth: {truth}"
    return 0.0, f"Incorrect. Predicted: {predicted}, Truth: {truth}"


def load_gsm8k_dataset(path_or_url: str, max_rows: int) -> List[Dict[str, Any]]:
    """Load a GSM8K-style dataset from a local file or URL.

    Expected format: JSON Lines with 'messages' and 'ground_truth' fields.

    Args:
        path_or_url: Local file path or HTTP(S) URL to the JSONL file
        max_rows: Maximum number of examples to load

    Returns:
        List of dataset rows (dicts with 'messages' and 'ground_truth')
    """
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        resp = httpx.get(path_or_url, timeout=30)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
    else:
        with open(path_or_url) as f:
            lines = f.readlines()

    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        rows.append(row)
        if len(rows) >= max_rows:
            break
    log(f"Loaded {len(rows)} examples from dataset")
    return rows
