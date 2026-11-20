PRIORITY = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3, "^": 4}
RIGHT_ASSOC = {"^"}
BINARY = {"+", "-", "*", "/", "^"}


def tokenize(expr: str):
    tokens: list[str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            start = i
            while i < len(expr) and (expr[i].isdigit() or expr[i] == "."):
                i += 1
            number = expr[start:i]
            try:
                float(number)
            except ValueError:
                raise ValueError(f"Некорректное число: {number!r}") from None
            tokens.append(number)
        elif ch in "+-":
            # оператор стоит там, где ожидается операнд -> он унарный
            unary = not tokens or tokens[-1] in PRIORITY or tokens[-1] == "("
            if unary:
                if ch == "-":
                    tokens.append("u-")
                # унарный плюс ничего не меняет, пропускаем
            else:
                tokens.append(ch)
            i += 1
        elif ch in "*/^()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"Недопустимый символ: {ch!r}")
    return tokens


def to_rpn(expr: str):
    output: list[str] = []
    stack: list[str] = []

    for token in tokenize(expr):
        if token not in PRIORITY and token not in "()":
            output.append(token)  # число
        elif token == "u-":
            stack.append(token)  # префиксный оператор ничего не вытесняет
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Лишняя закрывающая скобка")
            stack.pop()  # убираем "("
        else:
            while stack and stack[-1] != "(":
                top = PRIORITY[stack[-1]]
                cur = PRIORITY[token]
                if top > cur or (top == cur and token not in RIGHT_ASSOC):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)

    while stack:
        top = stack.pop()
        if top == "(":
            raise ValueError("Незакрытая скобка")
        output.append(top)
    return output


def evaluate_rpn(tokens: list[str]):
    stack: list[float] = []
    for token in tokens:
        if token == "u-":
            if not stack:
                raise ValueError("Некорректное выражение")
            stack.append(-stack.pop())
        elif token in BINARY:
            if len(stack) < 2:
                raise ValueError("Некорректное выражение")
            b = stack.pop()
            a = stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                if b == 0:
                    raise ZeroDivisionError("Деление на ноль")
                stack.append(a / b)
            else:
                stack.append(a**b)
        else:
            stack.append(float(token))
    if len(stack) != 1:
        raise ValueError("Некорректное выражение")
    return stack[0]


def calculate(expr: str):
    return evaluate_rpn(to_rpn(expr))


def main():
    while True:
        expr = input("Выражение (пусто - выход): ").strip()
        if not expr:
            break
        try:
            rpn = to_rpn(expr)
            result = evaluate_rpn(rpn)
        except (ValueError, ZeroDivisionError) as err:
            print(f"Ошибка: {err}")
            continue
        print("ОПЗ:", " ".join(rpn))
        print("Результат:", int(result) if result.is_integer() else result)


if __name__ == "__main__":
    main()