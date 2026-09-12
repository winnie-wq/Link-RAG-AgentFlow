'''`ast` 是 Python 内置抽象语法树模块，
可以把字符串代码解析成语法树节点对象，用来分析代码结构。'''
import ast 
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

'''
`isinstance(对象, 类)`:
语法，判断对象是不是该类的实例。
'''
def _calculate(node):


    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.BinOp):

        left = _calculate(node.left)
        right = _calculate(node.right)

        operator_type = type(node.op)

        if operator_type not in OPERATORS:
            raise ValueError("不支持该运算符")

        return OPERATORS[operator_type](
            left,
            right,
        )

    raise ValueError("非法数学表达式")


def calculator(expression: str):

    if not expression:
        raise ValueError("expression 不能为空")

    tree = ast.parse(
        expression,
        mode="eval",
    )

    result = _calculate(
        tree.body
    )

    return {
        "expression": expression,
        "result": result,
    }
