from src.moderator import ModerationConfig, moderate_text


def test_flags_ai_disclosure_and_spam():
    text = "As an AI language model, click here to buy now."
    result = moderate_text(text)
    assert result.flags["ai_disclosure"] is True
    assert result.flags["spam"] is True


def test_repetition_and_unique_word_ratio():
    text = "hello hello hello hello"
    config = ModerationConfig(max_repetition_ratio=0.2, min_unique_word_ratio=0.5)
    result = moderate_text(text, config)
    assert result.flags["high_repetition"] is True
    assert result.flags["low_unique_words"] is True


def test_sensitive_detection():
    text = "Please send your social security number and credit card."
    result = moderate_text(text)
    assert result.flags["sensitive"] is True
