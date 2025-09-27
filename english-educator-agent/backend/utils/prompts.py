"""
Prompt templates for agents.
"""

# Evaluator Agent Prompts
EVALUATOR_SYSTEM_PROMPT = """You are an expert English language evaluator following the CEFR framework.
Your task is to assess students' English proficiency through natural conversation."""

EVALUATOR_QUESTION_PROMPT = """Generate an appropriate evaluation question for the student.
Previous context: {context}
Question number: {question_num}
Generate a question that tests: {skill_area}"""

# Tutor Agent Prompts
TUTOR_LESSON_PROMPT = """Create a comprehensive lesson on {topic} for {level} level students.
Include: objectives, vocabulary, grammar focus, examples, and practice exercises."""

TUTOR_EXPLANATION_PROMPT = """Explain {concept} clearly for {level} level students.
Use simple language and provide practical examples."""

# Grammar Checker Prompts
GRAMMAR_CHECK_PROMPT = """Analyze this text for grammar errors: "{text}"
Student level: {level}
Provide corrections with explanations appropriate for their level."""

GRAMMAR_EXPLAIN_ERROR_PROMPT = """Explain this grammar error in detail:
Error type: {error_type}
Example: "{example}"
Student level: {level}"""

# Conversation Partner Prompts
CONVERSATION_SYSTEM_PROMPT = """You are a friendly English conversation partner.
Student level: {level}
Topic: {topic}
Be natural, encouraging, and adapt your language to their level."""

# Exercise Generator Prompts
EXERCISE_MULTIPLE_CHOICE_PROMPT = """Create {quantity} multiple choice questions about {topic} for {level} level.
Make them engaging and educational."""

EXERCISE_FILL_BLANK_PROMPT = """Create {quantity} fill-in-the-blank exercises for {topic} ({level} level).
Focus on practical language use."""

# Progress Tracker Prompts
PROGRESS_REPORT_PROMPT = """Analyze student progress and generate a comprehensive report.
Period: {period_days} days
Data: {data}
Provide insights, achievements, and recommendations."""

PROGRESS_GOALS_PROMPT = """Create a learning roadmap from {current_level} to {target_level}.
Timeframe: {months} months
Include milestones, weekly targets, and success indicators."""

# Common Templates
LEVEL_ASSESSMENT_PROMPT = """Based on this performance, assess the student's CEFR level:
{performance_data}
Provide level with confidence score and reasoning."""

FEEDBACK_TEMPLATE = """Provide encouraging feedback on:
{content}
Student level: {level}
Be specific, constructive, and motivating."""

# Prompt Helper Functions
def format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with provided variables."""
    return template.format(**kwargs)


def get_level_appropriate_language(level: str) -> dict:
    """Get language complexity guidelines for each level."""
    return {
        "A1": {
            "sentence_length": "very short, 5-8 words",
            "vocabulary": "basic, everyday words",
            "grammar": "simple present, basic structures"
        },
        "A2": {
            "sentence_length": "short, 8-12 words",
            "vocabulary": "common words and phrases",
            "grammar": "present, past, future; common patterns"
        },
        "B1": {
            "sentence_length": "moderate, 12-15 words",
            "vocabulary": "standard vocabulary, some idioms",
            "grammar": "various tenses, conditionals, passive"
        },
        "B2": {
            "sentence_length": "varied, 15-20 words",
            "vocabulary": "wide range, idiomatic expressions",
            "grammar": "complex structures, nuanced meanings"
        },
        "C1": {
            "sentence_length": "complex, 20+ words",
            "vocabulary": "sophisticated, precise word choice",
            "grammar": "advanced structures, subtle distinctions"
        },
        "C2": {
            "sentence_length": "highly varied and complex",
            "vocabulary": "near-native, nuanced vocabulary",
            "grammar": "mastery of all structures"
        }
    }.get(level, {"sentence_length": "moderate", "vocabulary": "standard", "grammar": "varied"})


def get_error_explanation_depth(level: str) -> str:
    """Get appropriate explanation depth for level."""
    depths = {
        "A1": "very simple, use basic language and clear examples",
        "A2": "simple, use common words and step-by-step",
        "B1": "moderate detail, use standard terminology",
        "B2": "detailed, use technical terms with explanations",
        "C1": "comprehensive, use precise terminology",
        "C2": "advanced, discuss nuances and exceptions"
    }
    return depths.get(level, "moderate detail")


# Common phrases for different contexts
ENCOURAGEMENT_PHRASES = [
    "Great job!",
    "You're making excellent progress!",
    "Keep up the good work!",
    "That's much better!",
    "You're improving every day!",
    "Well done!",
    "Fantastic effort!",
    "You've got this!"
]

ERROR_CORRECTION_PHRASES = [
    "Let's look at this together...",
    "Here's a small adjustment...",
    "You're close! Consider...",
    "Good try! The correct form is...",
    "Almost there! Just remember..."
]

LEVEL_UP_MESSAGES = {
    "A1_to_A2": "You've mastered the basics! Ready for the next challenge?",
    "A2_to_B1": "Great progress! You're becoming more confident!",
    "B1_to_B2": "Impressive! Your English is really developing!",
    "B2_to_C1": "Excellent work! You're approaching advanced level!",
    "C1_to_C2": "Outstanding! You're nearly at mastery level!"
}
