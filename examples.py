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
        "benefit": "Shows an editor how 'finally admits failure' turns a policy update into a settled verdict before the article begins.",
    },
    {
        "name": "Political debate questions",
        "a": "When will you stop the reckless spending that damaged the economy?",
        "b": "What is your plan for managing government expenditure going forward?",
        "topic": "Economic policy",
        "benefit": "Helps debate moderators spot loaded questions that embed blame before the candidate can answer.",
    },
    {
        "name": "Corporate press release vs. journalism",
        "a": "Company responsibly manages workforce transition amid market changes.",
        "b": "Company lays off 2,000 workers after missing quarterly targets.",
        "topic": "Corporate layoffs",
        "benefit": "Helps reporters distinguish corporate framing from a more direct news headline.",
    },
    {
        "name": "Health communication framing",
        "a": "Study confirms the harmful long-term effects of the food additive.",
        "b": "New study examines potential health effects of common food additive.",
        "topic": "Public health",
        "benefit": "Helps health writers avoid overstating what a study has established.",
    },
    {
        "name": "Article headline edit: investigation",
        "a": "Mayor finally admits the failed housing plan displaced families.",
        "b": "Mayor responds to investigation into housing plan and tenant displacement.",
        "topic": "Housing investigation",
        "benefit": "Gives editors a fast way to compare a sharper headline against a neutral version before publication.",
    },
    {
        "name": "Press release headline vs. reported headline",
        "a": "District restores classroom excellence after years of neglect.",
        "b": "District announces new classroom improvement plan after test score decline.",
        "topic": "Education policy",
        "benefit": "Shows how institutional copy can smuggle in a success story and a prior failure without proving either one.",
    },
    {
        "name": "Court story headline framing",
        "a": "Former executive fails to explain the missing investor funds.",
        "b": "Former executive questioned about disputed investor fund transfers.",
        "topic": "Legal reporting",
        "benefit": "Helps legal reporters avoid headlines that presuppose wrongdoing before the evidence is tested.",
    },
    {
        "name": "Public health headline framing",
        "a": "Agency finally stops hiding the vaccine side-effect reports.",
        "b": "Agency releases updated review of vaccine side-effect reports.",
        "topic": "Public health communication",
        "benefit": "Shows how a headline can imply concealment while a neutral version reports the same event without importing blame.",
    },
]

ARTICLE_EXAMPLES = [
    {
        "name": "City budget article draft",
        "text": (
            "City officials finally admitted that the downtown recovery plan has failed. "
            "Before the council approved another funding round, residents questioned why the agency kept ignoring neighborhood concerns. "
            "The mayor said the new proposal would restore trust in the planning process. "
            "Opposition members asked when the administration would stop blaming previous leaders for current delays. "
            "A public hearing is scheduled for next week."
        ),
    },
    {
        "name": "Corporate layoff article draft",
        "text": (
            "The company confirmed the damage caused by its expansion strategy after announcing 2,000 layoffs. "
            "Executives said they had managed to protect core research teams while reducing costs. "
            "Before the cuts were disclosed, employees had asked whether leadership was still hiding the scale of the shortfall. "
            "The firm said the workforce transition would position it for a return to sustainable growth."
        ),
    },
    {
        "name": "Public health explainer draft",
        "text": (
            "A new report confirms that the additive affected sleep quality in some participants. "
            "Researchers said the evidence still requires replication before regulators change guidance. "
            "When asked whether officials had stopped dismissing patient concerns, the agency said its review remained open. "
            "The study authors warned against treating early findings as settled medical advice."
        ),
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
        "why": "Show the Compare section. Paste these two headlines about the same story. Text A has factive ('admits') and iterative ('finally') triggers. Text B has none. This shows in 10 seconds how word choice embeds hidden assumptions.",
    },
    {
        "title": "The Media Literacy Score Demo",
        "sentence": "She finally stopped hiding the truth she knew all along.",
        "why": "Run this through the analyzer. Show the Media Literacy Score around 7-8/10 high load. Tell judges: 'We give presupposition density a number that anyone can understand.'",
    },
    {
        "title": "The Article Audit Demo",
        "sentence": "Load the city budget article draft in Article Lab.",
        "why": "Show that PragmaLens is not only a sentence toy. It scans a full article draft, ranks the riskiest sentences, and exports an assumption ledger a journalist or editor could use before publication.",
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
