import json
import math
from pathlib import Path


# Store leaderboard.json in the project root.
LEADERBOARD_FILE = (
    Path(__file__).resolve().parent.parent / "leaderboard.json"
)

MAX_SCORES = 5


def load_leaderboard():
    """
    Load the top scores from leaderboard.json.

    Returns an empty list if the file does not exist,
    is empty, contains invalid JSON, or contains invalid data.
    """

    if not LEADERBOARD_FILE.exists():
        return []

    try:
        if LEADERBOARD_FILE.stat().st_size == 0:
            return []

        with LEADERBOARD_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # The leaderboard must be stored as a list.
        if not isinstance(data, list):
            return []

        scores = []

        for score in data:
            # bool is technically an int in Python,
            # so explicitly reject it.
            if isinstance(score, (int, float)) and not isinstance(score, bool):
                score = float(score)

                # Only accept finite, non-negative times.
                if math.isfinite(score) and score >= 0:
                    scores.append(score)

        scores.sort()

        return scores[:MAX_SCORES]

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return []


def save_leaderboard(scores):
    """
    Save the fastest five scores to leaderboard.json.
    """

    # Clean and sort the supplied scores before saving.
    valid_scores = []

    for score in scores:
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            score = float(score)

            if math.isfinite(score) and score >= 0:
                valid_scores.append(score)

    valid_scores.sort()
    valid_scores = valid_scores[:MAX_SCORES]

    try:
        with LEADERBOARD_FILE.open("w", encoding="utf-8") as file:
            json.dump(valid_scores, file, indent=2)

    except OSError:
        # The game should not crash if the leaderboard
        # cannot be written.
        pass


def add_score(score):
    """
    Add a completed run to the leaderboard.

    Returns the updated top-five leaderboard.
    """

    scores = load_leaderboard()

    if isinstance(score, (int, float)) and not isinstance(score, bool):
        score = float(score)

        if math.isfinite(score) and score >= 0:
            scores.append(score)

    scores.sort()
    scores = scores[:MAX_SCORES]

    save_leaderboard(scores)

    return scores