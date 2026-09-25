"""
Vyom - Math/Physics Solver
Real exact computation via sympy (LLM guess nahi), LLM sirf explain karta hai.
"""

import sympy as sp


class MathSolver:
    def __init__(self, brain=None):
        self.brain = brain

    def solve_equation(self, equation_str, variable="x"):
        try:
            var = sp.symbols(variable)
            if "=" in equation_str:
                lhs, rhs = equation_str.split("=")
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation_str)
            solutions = sp.solve(expr, var)
            return {"ok": True, "solutions": [str(s) for s in solutions]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def evaluate(self, expression):
        try:
            result = sp.simplify(sp.sympify(expression))
            return {"ok": True, "result": str(result), "numeric": str(sp.N(result))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def differentiate(self, expression, variable="x"):
        try:
            var = sp.symbols(variable)
            expr = sp.sympify(expression)
            derivative = sp.diff(expr, var)
            return {"ok": True, "derivative": str(derivative)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def integrate(self, expression, variable="x"):
        try:
            var = sp.symbols(variable)
            expr = sp.sympify(expression)
            integral = sp.integrate(expr, var)
            return {"ok": True, "integral": str(integral)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def explain_with_llm(self, question, computed_result):
        if not self.brain:
            return str(computed_result)
        prompt = "Question: " + question + "\nExact computed result: " + str(computed_result) + "\nAb is result ko step-by-step explain karo."
        return self.brain.simple_ask(prompt)

    def solve_and_explain(self, question):
        if not self.brain:
            return "LLM brain not configured."

        extraction_prompt = "Is question se equation nikaal kar 'EQUATION: <equation>' format mein, ya expression ho to 'EVAL: <expression>' format mein, warna 'CONCEPT: <jawab>' format mein ek line output karo. Question: " + question
        extraction = self.brain.simple_ask(extraction_prompt).strip()

        if extraction.startswith("EQUATION:"):
            eq = extraction.replace("EQUATION:", "").strip()
            result = self.solve_equation(eq)
        elif extraction.startswith("EVAL:"):
            expr = extraction.replace("EVAL:", "").strip()
            result = self.evaluate(expr)
        else:
            return self.brain.reason_step_by_step(question)

        return self.explain_with_llm(question, result)
