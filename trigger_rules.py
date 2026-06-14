from dataclasses import dataclass


FACTIVE_VERBS = {
    "know",
    "realize",
    "discover",
    "find",
    "find out",
    "learn",
    "forget",
    "regret",
    "be aware",
    "understand",
    "notice",
    "remember",
    "see",
    "admit",
    "confirm",
    "acknowledge",
}

IMPLICATIVE_VERBS_POS = {"manage", "succeed", "remember", "bother"}
IMPLICATIVE_VERBS_NEG = {"fail", "forget", "neglect", "avoid"}

CHANGE_STATE_VERBS = {
    "stop",
    "start",
    "begin",
    "continue",
    "cease",
    "resume",
    "keep",
    "quit",
    "halt",
    "end",
    "initiate",
    "restart",
}

ITERATIVES = {"again", "still", "anymore", "yet", "back", "return", "repeat", "restore"}
CLEFT_TRIGGERS = ["it was", "it is", "what"]
TEMPORAL_CONJUNCTIONS = {"before", "after", "since", "when", "until", "while"}

TRIGGER_COLORS = {
    "factive": "#2563EB",
    "implicative": "#059669",
    "change_of_state": "#EA580C",
    "iterative": "#7C3AED",
    "definite_np": "#C2410C",
    "temporal": "#DC2626",
    "cleft": "#CA8A04",
}

TRIGGER_LABELS = {
    "factive": "Factive",
    "implicative": "Implicative",
    "change_of_state": "Change of State",
    "iterative": "Iterative",
    "definite_np": "Definite NP",
    "temporal": "Temporal Clause",
    "cleft": "Cleft",
}


@dataclass
class Presupposition:
    trigger_word: str
    trigger_type: str
    presupposition_str: str
    explanation: str
    span_start: int
    span_end: int
    verified: bool = True
    subtlety: int = 3
    significance: str = ""
    confidence: float = 0.75
    rule_name: str = ""
    rule_explanation: str = ""
    subject: str = ""
    complement: str = ""
    source: str = "rule_based"
