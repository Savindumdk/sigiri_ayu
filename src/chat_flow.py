"""Questionnaire state machine for the guided recommendation flow."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Stage(str, Enum):
    START = "start"
    ASK_CATEGORY = "ask_category"
    ASK_CONCERN = "ask_concern"
    ASK_TYPE = "ask_type"
    RECOMMEND = "recommend"
    FREE_CHAT = "free_chat"


CATEGORY_OPTIONS = [
    "Hair Care",
    "Face Care",
    "Body Care",
    "Lip Care",
    "Nails & Feet",
    "Just browsing",
]

CONCERN_OPTIONS: Dict[str, List[str]] = {
    "Hair Care": ["Dandruff", "Hair fall", "Dryness / damage", "Dullness / frizz", "Scalp build-up"],
    "Face Care": ["Acne / breakouts", "Dullness / uneven tone", "Dryness", "Oiliness", "Sensitivity / redness"],
    "Body Care": ["Dry skin", "Rough texture", "Glow / radiance", "Relaxation / aroma", "Intimate care"],
    "Lip Care": ["Dry / chapped lips", "Dullness", "Exfoliation"],
    "Nails & Feet": ["Weak / brittle nails", "Dry / cracked feet", "Foot roughness"],
    "Just browsing": ["Tell me about the brand", "Show popular products", "Recommend a gift"],
}

SKIN_TYPE_OPTIONS = {
    "Hair Care": ["Dry", "Oily", "Normal", "Mixed", "Sensitive scalp"],
    "Face Care": ["Dry", "Oily", "Normal", "Combination", "Sensitive"],
    "Body Care": ["Dry", "Oily", "Normal", "Sensitive"],
    "Lip Care": ["Dry", "Normal", "Sensitive"],
    "Nails & Feet": ["Dry", "Normal", "Sensitive"],
    "Just browsing": ["Skip"],
}


@dataclass
class FlowState:
    stage: Stage = Stage.START
    answers: Dict[str, str] = field(default_factory=dict)

    def reset(self) -> None:
        self.stage = Stage.START
        self.answers = {}


def next_stage(state: FlowState, choice: str) -> FlowState:
    """Advance the state machine given the user's choice for the current stage."""
    if state.stage == Stage.START:
        state.stage = Stage.ASK_CATEGORY
        return state
    if state.stage == Stage.ASK_CATEGORY:
        state.answers["category"] = choice
        state.stage = Stage.ASK_CONCERN
        return state
    if state.stage == Stage.ASK_CONCERN:
        state.answers["concern"] = choice
        state.stage = Stage.ASK_TYPE
        return state
    if state.stage == Stage.ASK_TYPE:
        state.answers["type"] = choice
        state.stage = Stage.RECOMMEND
        return state
    if state.stage == Stage.RECOMMEND:
        state.stage = Stage.FREE_CHAT
        return state
    return state


def build_recommendation_query(answers: Dict[str, str]) -> str:
    category = answers.get("category", "")
    concern = answers.get("concern", "")
    skin_type = answers.get("type", "")
    if category == "Just browsing":
        return f"The user is browsing and interested in: {concern}. Suggest relevant Sigiri Ayu products and briefly introduce them."
    parts = [f"Recommend the best Sigiri Ayu {category} products"]
    if concern:
        parts.append(f"for someone dealing with {concern.lower()}")
    if skin_type and skin_type.lower() != "skip":
        parts.append(f"with {skin_type.lower()} skin/scalp type")
    parts.append(
        "Suggest 2-3 specific products from the context and explain exactly why each one fits these needs, mentioning key ingredients and benefits."
    )
    return ". ".join(parts)


def concerns_for(category: str) -> List[str]:
    return CONCERN_OPTIONS.get(category, CONCERN_OPTIONS["Just browsing"])


def types_for(category: str) -> List[str]:
    return SKIN_TYPE_OPTIONS.get(category, ["Normal"])
