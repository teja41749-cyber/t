from typing import List, Dict, Any
from ..models.uml_model import UMLModel, UMLClass, UMLRelationship, RelationshipType, Attribute, Method

class MermaidConverter:
    def __init__(self):
        self.relationship_symbols = {
            RelationshipType.COMPOSITION: "*--",
            RelationshipType.AGGREGATION: "o--",
            RelationshipType.ASSOCIATION: "--",
            RelationshipType.INHERITANCE: "<|--"
        }

    def convert_to_mermaid(self, uml_model: UMLModel) -> str:
        """Convert UML model to Mermaid class diagram syntax."""
        if not uml_model.classes:
            return "classDiagram\n    note \"No classes found\""

        mermaid_lines = ["classDiagram"]

        # Add class definitions
        for cls in uml_model.classes:
            class_lines = self._format_mermaid_class(cls)
            mermaid_lines.extend(class_lines)

        # Add relationships
        for relationship in uml_model.relationships:
            relationship_line = self._format_mermaid_relationship(relationship)
            mermaid_lines.append(relationship_line)

        # Optimize layout if needed
        mermaid_lines = self._optimize_layout(mermaid_lines)

        return "\n    ".join(mermaid_lines)

    def _format_mermaid_class(self, cls: UMLClass) -> List[str]:
        """Format a single class in Mermaid syntax."""
        lines = [f"class {cls.name} {{"}]

        # Add attributes
        for attr in cls.attributes:
            attr_line = f"    {attr.visibility}{attr.name}: {attr.type}"
            if attr.is_static:
                attr_line = f"{attr_line} $static"
            lines.append(attr_line)

        # Add methods
        for method in cls.methods:
            params = ", ".join(method.parameters) if method.parameters else ""
            method_line = f"    {method.visibility}{method.name}({params}): {method.return_type}"
            if method.is_static:
                method_line = f"{method_line} $static"
            lines.append(method_line)

        lines.append("}")
        return lines

    def _format_mermaid_relationship(self, relationship: UMLRelationship) -> str:
        """Format a relationship in Mermaid syntax."""
        symbol = self.relationship_symbols.get(relationship.type, "--")
        multiplicity_source = f'"{relationship.multiplicity_source}"' if relationship.multiplicity_source else ""
        multiplicity_target = f'"{relationship.multiplicity_target}"' if relationship.multiplicity_target else ""
        label = f' : {relationship.label}' if relationship.label else ""

        rel_line = f"{relationship.source} {multiplicity_source} {symbol} {multiplicity_target} {relationship.target}{label}"
        return rel_line.strip()

    def _optimize_layout(self, mermaid_lines: List[str]) -> List[str]:
        """Optimize diagram layout by reordering classes to reduce line crossings."""
        # Simple optimization: place related classes closer together
        # This is a basic implementation - more sophisticated algorithms could be added

        class_names = []
        for line in mermaid_lines:
            if line.startswith("class ") and "{" not in line:
                class_name = line.split()[1]
                class_names.append(class_name)

        # For now, just return the original lines
        # More advanced layout optimization could be implemented here
        return mermaid_lines

    def validate_mermaid_syntax(self, mermaid_code: str) -> Dict[str, Any]:
        """Validate generated Mermaid syntax."""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # Basic syntax checks
        if not mermaid_code.startswith("classDiagram"):
            validation_result['errors'].append("Missing 'classDiagram' directive")
            validation_result['is_valid'] = False

        # Check for balanced braces
        open_braces = mermaid_code.count("{")
        close_braces = mermaid_code.count("}")
        if open_braces != close_braces:
            validation_result['errors'].append("Unbalanced braces in class definitions")
            validation_result['is_valid'] = False

        # Check for empty class definitions
        if re.search(r'class \w+ \{\s*\}', mermaid_code):
            validation_result['warnings'].append("Empty class definitions found")

        # Check for invalid relationship symbols
        valid_symbols = ["*--", "o--", "--", "<|--"]
        for line in mermaid_code.split('\n'):
            if "--" in line and not any(symbol in line for symbol in valid_symbols):
                validation_result['errors'].append(f"Invalid relationship symbol in line: {line.strip()}")
                validation_result['is_valid'] = False

        return validation_result

    def add_layout_direction(self, mermaid_code: str, direction: str = "TB") -> str:
        """Add layout direction to Mermaid diagram."""
        direction_map = {
            "TB": "Top to Bottom",
            "BT": "Bottom to Top",
            "LR": "Left to Right",
            "RL": "Right to Left"
        }

        if direction not in direction_map:
            direction = "TB"

        lines = mermaid_code.split('\n')
        lines.insert(1, f"    direction {direction}")
        return '\n'.join(lines)

    def export_to_formats(self, mermaid_code: str) -> Dict[str, str]:
        """Generate different export formats from Mermaid code."""
        return {
            'mermaid': mermaid_code,
            'svg_note': "SVG export requires Mermaid CLI or browser rendering",
            'png_note': "PNG export requires Mermaid CLI or browser rendering"
        }