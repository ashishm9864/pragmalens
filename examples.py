EXAMPLES = {
    "Politics": [
        "When will you fix the mess your policies created?",
        "Even Biden supporters admit the border situation worsened.",
        "We need to restore law and order to our streets.",
        "He finally admitted his administration's failures.",
        "America needs to return to its founding principles.",
        "When did politicians stop caring about ordinary people?",
        "The minister regretted that the warning signs were ignored.",
    ],
    "News Headlines": [
        "Tech CEO's failed promises anger investors.",
        "New study confirms damage from previous policies.",
        "Mayor stops the controversial rezoning plan.",
        "She manages to hold the coalition together.",
        "Before the collapse, the startup seemed unstoppable.",
        "New report confirms the damage done by previous policies.",
        "The agency finally stopped hiding the inspection failures.",
    ],
    "Everyday Speech": [
        "It was the overtime work that burned her out.",
        "He's back to his old habits again.",
        "Did you know that the project is underfunded?",
        "They managed to keep it secret.",
        "After he left the company, profits recovered.",
        "She managed to finish before the deadline.",
        "Maya realized that the budget had already been cut.",
    ],
    "Classic Philosophy": [
        "The present king of France is bald.",
        "Have you stopped lying to your clients?",
        "It was Oedipus who killed his father.",
        "John regrets that he accepted the offer.",
        "The present king of France is not bald.",
        "It was the butler who stole the jewels.",
    ],
}

DEMO_SENTENCES = [
    "The present king of France is bald.",
    "When did politicians stop caring about ordinary people?",
    "She managed to finish before the deadline.",
    "New report confirms the damage done by previous policies.",
]

COMPARE_PAIRS = [
    {
        "name": "Same story, different framing",
        "a": "Government finally admits failure of long-running infrastructure policy.",
        "b": "Government announces new review of infrastructure investment programme.",
        "topic": "Infrastructure policy",
    },
    {
        "name": "Political debate questions",
        "a": "When will you stop the reckless spending that damaged the economy?",
        "b": "What is your plan for managing government expenditure going forward?",
        "topic": "Economic policy",
    },
    {
        "name": "Corporate press release vs. journalism",
        "a": "Company responsibly manages workforce transition amid market changes.",
        "b": "Company lays off 2,000 workers after missing quarterly targets.",
        "topic": "Corporate layoffs",
    },
    {
        "name": "Health communication framing",
        "a": "Study confirms the harmful long-term effects of the food additive.",
        "b": "New study examines potential health effects of common food additive.",
        "topic": "Public health",
    },
]

KILLER_DEMOS = [
    {
        "title": "Classic credibility",
        "sentence": "The present king of France is bald.",
        "why": "Shows the philosophical roots of presupposition theory.",
    },
    {
        "title": "Loaded question",
        "sentence": "When did politicians stop caring about ordinary people?",
        "why": "Shows how questions can smuggle in an accusation.",
    },
    {
        "title": "Subtle everyday language",
        "sentence": "She managed to finish before the deadline.",
        "why": "Shows an implicit attempt and a temporal background assumption.",
    },
    {
        "title": "News headline framing",
        "sentence": "New report confirms the damage done by previous policies.",
        "why": "Shows how headlines can treat contested claims as settled background.",
    },
    {
        "title": "Judge interaction",
        "sentence": "Type your own sentence into the input box.",
        "why": "Shows confidence that the system is interactive, not pre-scripted.",
    },
    {
        "title": "The Compare Headlines Demo",
        "sentence": "Text A: 'Government finally admits failure.' vs Text B: 'Government announces new review.'",
        "why": "Show the Compare tab. Paste these two headlines about the same story. Text A has factive ('admits') and implicative ('finally') triggers. Text B has none. This shows in 10 seconds how word choice embeds hidden assumptions.",
    },
    {
        "title": "The Media Literacy Score Demo",
        "sentence": "When did politicians stop caring about ordinary people?",
        "why": "Run this through the analyzer. Show the Media Literacy Score (should be 7-8/10 high load). Tell judges: 'We give presupposition density a number that anyone can understand.'",
    },
]

EVALUATION_CASES = [
    {
        "sentence": "The present king of France is bald.",
        "expected": {"definite_np"},
    },
    {
        "sentence": "Have you stopped lying to your clients?",
        "expected": {"change_of_state"},
    },
    {
        "sentence": "He knows that the company lied to investors.",
        "expected": {"factive"},
    },
    {
        "sentence": "They managed to cover it up again.",
        "expected": {"implicative", "iterative"},
    },
    {
        "sentence": "It was the working class that bore the burden.",
        "expected": {"cleft", "definite_np"},
    },
    {
        "sentence": "Before the merger collapsed, profits were strong.",
        "expected": {"temporal"},
    },
    {
        "sentence": "After he left the company, profits recovered.",
        "expected": {"temporal"},
    },
    {
        "sentence": "John regrets that he accepted the offer.",
        "expected": {"factive"},
    },
    {
        "sentence": "She managed to finish before the deadline.",
        "expected": {"implicative", "temporal"},
    },
    {
        "sentence": "He's back to his old habits again.",
        "expected": {"iterative"},
    },
]
