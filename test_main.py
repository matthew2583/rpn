import pytest

from main import calculate, evaluate_rpn, to_rpn, tokenize


def rpn(expr: str):
    return " ".join(to_rpn(expr))


def test_tokenize_basic():
    assert tokenize("12 + 3.5*(2)") == ["12", "+", "3.5", "*", "(", "2", ")"]


def test_tokenize_unary_minus():
    assert tokenize("-1") == ["u-", "1"]
    assert tokenize("2*-3") == ["2", "*", "u-", "3"]
    assert tokenize("(-1)") == ["(", "u-", "1", ")"]
    assert tokenize("1-2") == ["1", "-", "2"]


def test_tokenize_unary_plus_ignored():
    assert tokenize("+5") == ["5"]


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1+2", "1 2 +"),
        ("1+2*3", "1 2 3 * +"),
        ("(1+2)*3", "1 2 + 3 *"),
        ("1-2-3", "1 2 - 3 -"),  # левая ассоциативность
        ("8/4/2", "8 4 / 2 /"),
        ("2^3^2", "2 3 2 ^ ^"),  # правая ассоциативность
        ("3+4*2/(1-5)^2^3", "3 4 2 * 1 5 - 2 3 ^ ^ / +"),
        ("-2^2", "2 2 ^ u-"),
        ("2^-2", "2 2 u- ^"),
        ("2*-3", "2 3 u- *"),
        ("((1))", "1"),
    ],
)
def test_to_rpn(expr, expected):
    assert rpn(expr) == expected


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1+2", 3),
        ("2+2*2", 6),
        ("(2+2)*2", 8),
        ("10/4", 2.5),
        ("2^10", 1024),
        ("2^3^2", 512),
        ("-2^2", -4),
        ("(-2)^2", 4),
        ("2^-1", 0.5),
        ("--3", 3),
        ("1.5+2.5", 4),
        ("  7 -  2 ", 5),
    ],
)
def test_calculate(expr, expected):
    assert calculate(expr) == pytest.approx(expected)


def test_evaluate_rpn_directly():
    assert evaluate_rpn(["3", "4", "+", "2", "*"]) == 14


@pytest.mark.parametrize("expr", ["(1+2", "1+2)", ")(", "(()"])
def test_unbalanced_parentheses(expr):
    with pytest.raises(ValueError):
        to_rpn(expr)


@pytest.mark.parametrize("expr", ["2 +", "* 3", "2 3", "", "()", "1 + * 2"])
def test_malformed_expression(expr):
    with pytest.raises(ValueError):
        calculate(expr)


@pytest.mark.parametrize("expr", ["2 & 3", "abc", "1..2 + 1"])
def test_invalid_input(expr):
    with pytest.raises(ValueError):
        calculate(expr)


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("1/(2-2)")