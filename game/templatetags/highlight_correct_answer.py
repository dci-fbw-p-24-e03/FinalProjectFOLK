import re
from django import template

register = template.Library()

@register.filter(name='highlight_correct')
def highlight_correct(text, correct):
    """
    Highlights all occurrences (case-insensitive) of the correct answer with correct-answer class.
    """
    if not correct:
        return text
    pattern = re.escape(correct)
    highlighted = re.sub(pattern,
                        f'<span class="correct-answer">{correct}</span>',
                        text,
                        flags=re.IGNORECASE)
    return highlighted

@register.filter(name='highlight_wrong')
def highlight_wrong(text, wrong):
    """
    Highlights all occurrences (case-insensitive) of the wrong answer with wrong-answer class.
    """
    if not wrong:
        return text
    pattern = re.escape(wrong)
    highlighted = re.sub(pattern,
                        f'<span class="wrong-answer">{wrong}</span>',
                        text,
                        flags=re.IGNORECASE)
    return highlighted

# Usage in template:
# {{ text|highlight_correct:correct_answer|highlight_wrong:wrong_answer }}