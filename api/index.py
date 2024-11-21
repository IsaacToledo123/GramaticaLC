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
        left = self.factor()
        while self._peek() in ('*', '/'):
            operator = self._consume()
            right = self.factor()
            if operator == '/' and right.get("número") == '0':
                raise ValueError("División entre 0 no permitida.")
            left = {
                "operación": operator,
                "valores": [left, right]
            }
        return left

    def factor(self):
        if self._peek().replace('.', '', 1).isdigit():
            value = self._consume()
            return {"número": value}
        elif self._peek() == '(':
            self._consume()
            expr = self.expr()
            self._consume()
            return expr
        else:
            raise ValueError("Token inesperado")

    def _peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def _consume(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    @staticmethod
    def classify_tokens(expression):
        tokens = re.findall(r'\d+\.\d+|\d+|[()+\-*/]', expression)
        classified = []
        for token in tokens:
            if token.isdigit():
                classified.append({"token": token, "tipo": "Número entero"})
            elif re.match(r'\d+\.\d+', token):
                classified.append({"token": token, "tipo": "Número flotante"})
            elif token == '+':
                classified.append({"token": token, "tipo": "Operador: suma"})
            elif token == '-':
                classified.append({"token": token, "tipo": "Operador: resta"})
            elif token == '*':
                classified.append({"token": token, "tipo": "Operador: multiplicación"})
            elif token == '/':
                classified.append({"token": token, "tipo": "Operador: división"})
            elif token == '(':
                classified.append({"token": token, "tipo": "Paréntesis: apertura"})
            elif token == ')':
                classified.append({"token": token, "tipo": "Paréntesis: cierre"})
        return classified


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    expression = data.get("expression", "")
    try:
        parser = Parser(expression)
        tree = parser.parse()
        tokens = Parser.classify_tokens(expression)
        return jsonify({"arbol": tree, "tokens": tokens})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
