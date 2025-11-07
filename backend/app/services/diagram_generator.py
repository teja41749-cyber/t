import re

def _safe_name(name: str) -> str:
    # keep only letters/digits/underscore, no spaces or punctuation
    name = re.sub(r'[^0-9A-Za-z_]', '_', (name or '').strip())
    if not name:
        name = 'ClassX'
    if name[0].isdigit():
        name = '_' + name
    return name

class DiagramGenerator:
    def convert_to_mermaid(self, uml_model: dict) -> str:
        lines = ["classDiagram"]

        # ---- classes ----
        for cls in uml_model.get("classes", []):
            cname = _safe_name(cls.get('name', 'ClassX'))
            members = []

            # attributes: "name: Type" -> "+Type name"
            for a in cls.get("attributes", []):
                if ":" in a:
                    name, typ = [p.strip() for p in a.split(":", 1)]
                    members.append(f"  +{typ} {name}")
                else:
                    members.append(f"  +{a}")

            # methods already look like "foo()"
            for m in cls.get("methods", []):
                members.append(f"  +{m}")

            if members:
                lines.append(f"class {cname}{{")
                lines.extend(members)
                lines.append("}")
            else:
                # ⚠️ empty class → no braces
                lines.append(f"class {cname}")

        # ---- relationships ----
        for rel in uml_model.get("relationships", []):
            src = _safe_name(rel["source"])
            tgt = _safe_name(rel["target"])
            label = rel.get("label", "")
            ms = rel.get("multiplicity_source", "")
            mt = rel.get("multiplicity_target", "")
            arrow = {
                "COMPOSITION": "*--",
                "AGGREGATION": "o--",
                "ASSOCIATION": "--",
                "INHERITANCE": "<|--"
            }.get(rel.get("type", "ASSOCIATION"), "--")
            left = f' "{ms}"' if ms else ""
            right = f' "{mt}"' if mt else ""
            lines.append(f"{src}{left} {arrow}{right} {tgt} : {label}".rstrip())

        return "\n".join(lines)
