"""
Vyom - Chemistry Solver
Exact computation (LLM guess nahi) - periodic table, molecular weight, equation balancing.
"""

import re
from fractions import Fraction

PERIODIC_TABLE = {
    "H": {"name": "Hydrogen", "number": 1, "mass": 1.008},
    "He": {"name": "Helium", "number": 2, "mass": 4.0026},
    "Li": {"name": "Lithium", "number": 3, "mass": 6.94},
    "Be": {"name": "Beryllium", "number": 4, "mass": 9.0122},
    "B": {"name": "Boron", "number": 5, "mass": 10.81},
    "C": {"name": "Carbon", "number": 6, "mass": 12.011},
    "N": {"name": "Nitrogen", "number": 7, "mass": 14.007},
    "O": {"name": "Oxygen", "number": 8, "mass": 15.999},
    "F": {"name": "Fluorine", "number": 9, "mass": 18.998},
    "Ne": {"name": "Neon", "number": 10, "mass": 20.180},
    "Na": {"name": "Sodium", "number": 11, "mass": 22.990},
    "Mg": {"name": "Magnesium", "number": 12, "mass": 24.305},
    "Al": {"name": "Aluminium", "number": 13, "mass": 26.982},
    "Si": {"name": "Silicon", "number": 14, "mass": 28.085},
    "P": {"name": "Phosphorus", "number": 15, "mass": 30.974},
    "S": {"name": "Sulfur", "number": 16, "mass": 32.06},
    "Cl": {"name": "Chlorine", "number": 17, "mass": 35.45},
    "Ar": {"name": "Argon", "number": 18, "mass": 39.948},
    "K": {"name": "Potassium", "number": 19, "mass": 39.098},
    "Ca": {"name": "Calcium", "number": 20, "mass": 40.078},
    "Fe": {"name": "Iron", "number": 26, "mass": 55.845},
    "Cu": {"name": "Copper", "number": 29, "mass": 63.546},
    "Zn": {"name": "Zinc", "number": 30, "mass": 65.38},
    "Ag": {"name": "Silver", "number": 47, "mass": 107.868},
    "I": {"name": "Iodine", "number": 53, "mass": 126.904},
    "Ba": {"name": "Barium", "number": 56, "mass": 137.327},
    "Au": {"name": "Gold", "number": 79, "mass": 196.967},
    "Hg": {"name": "Mercury", "number": 80, "mass": 200.592},
    "Pb": {"name": "Lead", "number": 82, "mass": 207.2},
    "U": {"name": "Uranium", "number": 92, "mass": 238.029},
    "Br": {"name": "Bromine", "number": 35, "mass": 79.904},
    "Mn": {"name": "Manganese", "number": 25, "mass": 54.938},
    "Ni": {"name": "Nickel", "number": 28, "mass": 58.693},
    "Sn": {"name": "Tin", "number": 50, "mass": 118.710},
    "Pt": {"name": "Platinum", "number": 78, "mass": 195.084},
}


def parse_formula(formula):
    def multiply_dict(d, factor):
        return {k: v * factor for k, v in d.items()}

    def merge(d1, d2):
        result = dict(d1)
        for k, v in d2.items():
            result[k] = result.get(k, 0) + v
        return result

    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
    stack = [{}]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append({})
        elif tok == ")":
            group = stack.pop()
            i += 1
            count = 1
            if i < len(tokens) and tokens[i].isdigit():
                count = int(tokens[i])
            else:
                i -= 1
            stack[-1] = merge(stack[-1], multiply_dict(group, count))
        elif tok.isdigit():
            pass
        else:
            count = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                count = int(tokens[i + 1])
                i += 1
            stack[-1] = merge(stack[-1], {tok: count})
        i += 1

    return stack[0]


class ChemistrySolver:
    def molecular_weight(self, formula):
        try:
            atoms = parse_formula(formula)
            total = 0.0
            breakdown = {}
            for symbol, count in atoms.items():
                if symbol not in PERIODIC_TABLE:
                    return {"ok": False, "error": "Unknown element: " + symbol}
                mass = PERIODIC_TABLE[symbol]["mass"] * count
                total += mass
                breakdown[symbol] = {"count": count, "mass": round(mass, 3)}
            return {"ok": True, "formula": formula, "molecular_weight": round(total, 3), "breakdown": breakdown}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def moles_to_grams(self, moles, formula):
        mw = self.molecular_weight(formula)
        if not mw["ok"]:
            return mw
        return {"ok": True, "grams": round(moles * mw["molecular_weight"], 4)}

    def grams_to_moles(self, grams, formula):
        mw = self.molecular_weight(formula)
        if not mw["ok"]:
            return mw
        return {"ok": True, "moles": round(grams / mw["molecular_weight"], 6)}

    def molarity(self, moles, volume_liters):
        if volume_liters <= 0:
            return {"ok": False, "error": "Volume must be positive."}
        return {"ok": True, "molarity_M": round(moles / volume_liters, 6)}

    def balance_equation(self, reactants, products):
        try:
            import sympy as sp

            compounds = reactants + products
            parsed = [parse_formula(c) for c in compounds]
            elements = sorted(set(el for p in parsed for el in p))

            matrix = []
            for el in elements:
                row = []
                for idx, p in enumerate(parsed):
                    count = p.get(el, 0)
                    if idx >= len(reactants):
                        count = -count
                    row.append(count)
                matrix.append(row)

            M = sp.Matrix(matrix)
            null_space = M.nullspace()

            if not null_space:
                return {"ok": False, "error": "Equation balance nahi ho saka."}

            solution = null_space[0]
            denominators = [Fraction(str(x)).limit_denominator().denominator for x in solution]
            lcm = 1
            for d in denominators:
                lcm = lcm * d // __import__("math").gcd(lcm, d)
            coeffs = [int(x * lcm) for x in solution]

            if any(c < 0 for c in coeffs) and all(c <= 0 for c in coeffs):
                coeffs = [-c for c in coeffs]

            reactant_coeffs = coeffs[:len(reactants)]
            product_coeffs = coeffs[len(reactants):]

            balanced_lhs = " + ".join((str(c) if c != 1 else "") + r for c, r in zip(reactant_coeffs, reactants))
            balanced_rhs = " + ".join((str(c) if c != 1 else "") + p for c, p in zip(product_coeffs, products))

            return {
                "ok": True,
                "reactant_coefficients": reactant_coeffs,
                "product_coefficients": product_coeffs,
                "balanced_equation": balanced_lhs + " -> " + balanced_rhs,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def ph_from_concentration(self, h_concentration):
        import math
        if h_concentration <= 0:
            return {"ok": False, "error": "Concentration must be positive."}
        return {"ok": True, "pH": round(-math.log10(h_concentration), 3)}
