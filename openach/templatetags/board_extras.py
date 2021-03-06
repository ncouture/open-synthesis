from django.template.defaulttags import register
from openach.models import Evaluation, Eval
import logging
import collections
import math


logger = logging.getLogger(__name__)


@register.simple_tag
def get_detail(dictionary, evidence_id, hypothesis_id):
    """Returns the evaluation Eval for a given hypothesis and piece of evidence"""
    return dictionary.get((evidence_id, hypothesis_id))


@register.filter
def detail_name(value):
    if value:
        return next(e[1] for e in Evaluation.EVALUATION_OPTIONS if e[0] == value.value)
    else:
        return 'No Assessments'


@register.filter
def detail_classname(value):
    mapping = {
        None: "eval-no-assessments",
        Eval.consistent: "eval-consistent",
        Eval.inconsistent: "eval-inconsistent",
        Eval.very_inconsistent: "eval-very-inconsistent",
        Eval.very_consistent: "eval-very-consistent",
        Eval.not_applicable: "eval-not-applicable",
        Eval.neutral: "eval-neutral"
    }
    return mapping.get(value)


@register.simple_tag
def get_source_tags(dictionary, source_id, tag_id):
    """Performs a dictionary lookup, returning None if the key is not in the dictionary"""
    return dictionary.get((source_id, tag_id))


DisputeLevel = collections.namedtuple('DisputeLevel', ['max_level', 'name', 'css_class'])
_dispute_levels = [
    DisputeLevel(max_level=0.5, name='Consensus', css_class='disagree-consensus'),
    DisputeLevel(max_level=1.5, name='Mild Dispute', css_class='disagree-mild-dispute'),
    DisputeLevel(max_level=2.0, name='Large Dispute', css_class='disagree-large-dispute'),
    DisputeLevel(max_level=math.inf, name='Extreme Dispute', css_class='disagree-extreme-dispute'),
]


def _dispute_level(value):
    return list(filter(lambda x: value < x.max_level, _dispute_levels))[0]


@register.filter
def disagreement_category(value):
    return 'No Assessments' if value is None else _dispute_level(value).name


@register.filter
def disagreement_style(value):
    return 'disagree-no-assessments' if value is None else _dispute_level(value).css_class


@register.filter
def bootstrap_alert(tags):
    """
    If value is a Django message level, returns the corresponding bootstrap alert css class. Assumes a single tag
    for the message. See https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-tags
    """
    mapping = {
        'debug': 'alert-info',
        'info': 'alert-info',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-error',
    }
    return mapping[tags] if tags in mapping else tags


@register.filter
def board_url(board):
    """Return the URL for the board, including the slug if available."""
    # In the future, we might just want to directly use get_absolute_url in the template. However, this extra level
    # of indirection gives us some additional flexibility
    return board.get_absolute_url()
