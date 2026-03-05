"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Boundary case: item_id and learner_id differ (learner_id=2, item_id=1).

    When filtering by item_id=1 the interaction should still be returned
    regardless of the learner_id value.
    """
    interactions = [_make_log(1, 2, 1)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].learner_id == 2
    assert result[0].item_id == 1


def test_filter_returns_empty_when_no_item_id_matches() -> None:
    """Edge case: item_id is provided but no log in the list has that item_id.

    The filter must return an empty list, not raise and not return unrelated logs.
    """
    interactions = [_make_log(1, 1, 10), _make_log(2, 2, 20)]
    result = _filter_by_item_id(interactions, 99)
    assert result == []


def test_filter_returns_all_matching_when_multiple_logs_share_item_id() -> None:
    """Edge case: more than one log shares the requested item_id.

    All matching logs must be returned and none must be dropped.
    """
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 9),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(log.item_id == 5 for log in result)
    returned_ids = {log.id for log in result}
    assert returned_ids == {1, 2, 3}


def test_filter_single_element_list_match() -> None:
    """Boundary: a list with exactly one element whose item_id matches.

    The single-element result must equal the original one-element list.
    """
    interactions = [_make_log(1, 1, 7)]
    result = _filter_by_item_id(interactions, 7)
    assert result == interactions


def test_filter_single_element_list_no_match() -> None:
    """Boundary: a list with exactly one element whose item_id does not match.

    The result must be empty, not the original list.
    """
    interactions = [_make_log(1, 1, 7)]
    result = _filter_by_item_id(interactions, 8)
    assert result == []


def test_filter_with_item_id_zero_is_not_treated_as_none() -> None:
    """Edge case: item_id=0 is falsy in Python but must not behave like None.

    The function must filter on 0 rather than return all interactions.
    """
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, 1)]
    result = _filter_by_item_id(interactions, 0)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].item_id == 0
