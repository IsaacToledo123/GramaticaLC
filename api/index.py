from flask import Flask, request, jsonify
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


class Parser:
    def __init__(self, expression):
        self.tokens = re.findall(r'\d+\.\d+|\d+|[()+\-*/]', expression)
        self.index = 0

    def parse(self):
        return self.expr()

    def expr(self):
        # Parse a term and optionally add/subtract more terms
        left = self.term()
        while self._peek() in ('+', '-'):
            operator = self._consume()
            right = self.term()
            left = {
                "operación": operator,
                "valores": [left, right]
            }
        return left

    def term(self):
        # Parse a factor and optionally multiply/divide more factors
        left = self.factor()
        while self._peek() in ('*', '/'):
            operator = self._consume()
            right = self.factor()
            left = {
                "operación": operator,
                "valores": [left, right]
            }
        return left

    def factor(self):
        # Parse a number or a parenthesized expression
        if self._peek().replace('.', '', 1).isdigit():
            value = self._consume()
            return {"número": value}
        elif self._peek() == '(':
            self._consume()  # Consume '('
            expr = self.expr()
            self._consume()  # Consume ')'
            return expr
        else:
            raise ValueError("Token inesperado")

    def _peek(self):
        # Peek at the current token
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def _consume(self):
        # Consume the current token
        token = self.tokens[self.index]
        self.index += 1
        return token

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    expression = data.get("expression", "")
    try:
        parser = Parser(expression)
        tree = parser.parse()
        return jsonify({"arbol": tree})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
