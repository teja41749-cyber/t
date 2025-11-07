from app.utils.text_preprocessing import clean_text
import re

def _title(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s

def _singular(word: str) -> str:
    # very simple singular form
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word

class NLPProcessor:
    def process_requirements(self, text: str):
        t = clean_text(text).lower()

        uml = {
            "classes": [
                {"name": "User", "attributes": ["username: String", "email: String"], "methods": ["login()", "logout()"]},
                {"name": "Account", "attributes": ["balance: Float"], "methods": ["deposit()", "withdraw()"]}
            ],
            "relationships": [
                {"source": "User", "target": "Account", "type": "COMPOSITION",
                 "multiplicity_source": "1", "multiplicity_target": "1..*", "label": "contains"}
            ]
        }

        # detect “user(s) can <verb> <object>”
        pattern = re.compile(r"\busers?\s+can\s+([a-z]+)(?:\s+([a-z]+))?", re.IGNORECASE)
        methods = set(["login()", "logout()"])

        for verb, obj in pattern.findall(t):
            method = verb
            if obj and obj.isalpha():
                method += _title(obj)
            methods.add(f"{method}()")

        # update user methods
        for c in uml["classes"]:
            if c["name"].lower() == "user":
                base = ["login()", "logout()"]
                extra = [m for m in sorted(methods) if m not in base]
                c["methods"] = base + extra

        # detect object names for new classes
        objects = set()
        for _, obj in pattern.findall(t):
            if obj and obj.isalpha():
                base = _singular(obj.lower())
                if base not in ["account", "cart", "product", "order"]:
                    objects.add(_title(base))

        for name in sorted(objects):
            if not any(c["name"].lower() == name.lower() for c in uml["classes"]):
                uml["classes"].append({"name": name, "attributes": [], "methods": []})

        return uml
