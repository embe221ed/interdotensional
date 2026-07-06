import pytest

from interdotensional.tokens import (
    find_unresolved_tokens,
    flatten_dict,
    substitute_tokens,
)


class TestSubstituteTokens:
    def test_simple_string(self):
        assert substitute_tokens("$red$", {"red": "#f00"}) == "#f00"

    def test_multiple_tokens_in_one_string(self):
        result = substitute_tokens("$a$ and $b$", {"a": "1", "b": "2"})
        assert result == "1 and 2"

    def test_unknown_token_left_as_is(self):
        assert substitute_tokens("$missing$", {}) == "$missing$"

    def test_nested_structures(self):
        data = {"x": ["$red$", {"y": "$blue$"}], "z": "plain"}
        result = substitute_tokens(data, {"red": "#f00", "blue": "#00f"})
        assert result == {"x": ["#f00", {"y": "#00f"}], "z": "plain"}

    def test_dotted_token_names(self):
        assert substitute_tokens("$git.add$", {"git.add": "X"}) == "X"

    def test_non_string_leaves_pass_through(self):
        data = {"n": 3, "f": 1.5, "b": True, "none": None}
        assert substitute_tokens(data, {}) == data

    def test_non_string_token_value_is_stringified(self):
        # Regression: unquoted YAML palette values parse as ints; the re.sub
        # replacer used to return them raw and crash with TypeError.
        assert substitute_tokens("$n$", {"n": 123456}) == "123456"

    def test_original_data_not_mutated(self):
        data = {"x": "$red$"}
        substitute_tokens(data, {"red": "#f00"})
        assert data == {"x": "$red$"}


class TestFindUnresolvedTokens:
    def test_clean_data(self):
        assert find_unresolved_tokens({"x": "#f00"}) == []

    def test_dict_path(self):
        assert find_unresolved_tokens({"a": {"b": "$t$"}}) == [("a.b", "$t$")]

    def test_list_path(self):
        assert find_unresolved_tokens({"a": ["ok", "$t$"]}) == [("a[1]", "$t$")]

    def test_multiple_in_one_string(self):
        found = find_unresolved_tokens("$a$ $b$")
        assert [token for _, token in found] == ["$a$", "$b$"]


class TestFlattenDict:
    def test_flat_stays_flat(self):
        assert flatten_dict({"a": 1}) == {"a": 1}

    def test_nested(self):
        assert flatten_dict({"git": {"add": "X", "rm": "Y"}}) == {
            "git.add": "X",
            "git.rm": "Y",
        }

    def test_deep_nesting(self):
        assert flatten_dict({"a": {"b": {"c": 1}}}) == {"a.b.c": 1}

    def test_custom_separator(self):
        assert flatten_dict({"a": {"b": 1}}, sep="/") == {"a/b": 1}

    def test_non_dict_leaves(self):
        assert flatten_dict({"a": [1, 2], "b": None}) == {"a": [1, 2], "b": None}
