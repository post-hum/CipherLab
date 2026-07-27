import pytest

from cipherlab.stats.chi_squared import chi_squared_stat
from cipherlab.stats.ic import index_of_coincidence


def test_ic_all_same_letter_is_one():
    assert index_of_coincidence("aaaa") == pytest.approx(1.0)


def test_ic_known_hand_calculated_value():
    # "abab": A=2,B=2, N=4 -> IC = (2*1 + 2*1) / (4*3) = 4/12
    assert index_of_coincidence("abab") == pytest.approx(4 / 12)


def test_ic_empty_or_single_char_is_zero():
    assert index_of_coincidence("") == 0.0
    assert index_of_coincidence("a") == 0.0


def test_chi_squared_zero_when_matches_expected_exactly():
    text = "abab"  # 2 a, 2 b из 4 символов
    expected = {"a": 0.5, "b": 0.5}
    assert chi_squared_stat(text, expected) == pytest.approx(0.0)


def test_chi_squared_positive_when_distribution_differs():
    text = "aaab"  # сильно отличается от равномерного распределения
    expected = {"a": 0.5, "b": 0.5}
    assert chi_squared_stat(text, expected) > 0.0


def test_chi_squared_empty_text_is_infinite():
    assert chi_squared_stat("", {"a": 1.0}) == float("inf")
