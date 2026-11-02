import random

ENCOURAGEMENTS = [
    "Awesome!",
    "Nice one!",
    "Keep it up!",
    "You're on a roll!",
    "Great job!",
]


def encouragement(completed: int, target: int) -> str:
    if completed >= target:
        return "All done — fantastic work!"
    return random.choice(ENCOURAGEMENTS)
