from typing import Dict, Any, List
import logging
from ..models.uml_model import UMLModel
from ..utils.mermaid_converter import MermaidConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiagramGenerator:
    def __init__(self):
        """Initialize diagram generator."""
        self.mermaid_converter = MermaidConverter()

    def generate_diagram(self, uml_model: UMLModel, format_type: str = "mermaid") -> Dict[str, Any]:
        """
        Generate diagram in specified format from UML model.

        Args:
            uml_model: UML model structure
            format_type: Output format (mermaid, svg, png)

        Returns:
            Dictionary containing diagram code and metadata
        """
        try:
            logger.info(f"Generating diagram in {format_type} format")

            if format_type == "mermaid":
                return self._generate_mermaid_diagram(uml_model)
            else:
                return {
                    'error': f'Format {format_type} not yet supported',
                    'supported_formats': ['mermaid']
                }

        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return {
                'error': f'Diagram generation failed: {str(e)}',
                'format': format_type
            }

    def _generate_mermaid_diagram(self, uml_model: UMLModel) -> Dict[str, Any]:
        """Generate Mermaid class diagram."""
        # Convert to Mermaid syntax
        mermaid_code = self.mermaid_converter.convert_to_mermaid(uml_model)

        # Validate syntax
        validation_result = self.mermaid_converter.validate_mermaid_syntax(mermaid_code)

        # Add layout direction
        mermaid_with_layout = self.mermaid_converter.add_layout_direction(mermaid_code, "TB")

        return {
            'format': 'mermaid',
            'code': mermaid_with_layout,
            'validation': validation_result,
            'metadata': {
                'class_count': len(uml_model.classes),
                'relationship_count': len(uml_model.relationships),
                'layout_direction': 'TB'
            },
            'export_formats': self.mermaid_converter.export_to_formats(mermaid_with_layout)
        }

    def update_diagram(self, uml_model: UMLModel, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply changes to UML model and regenerate diagram.

        Args:
            uml_model: Current UML model
            changes: List of changes to apply

        Returns:
            Updated diagram
        """
        try:
            # Apply changes to model
            for change in changes:
                self._apply_change(uml_model, change)

            # Regenerate diagram
            return self.generate_diagram(uml_model, "mermaid")

        except Exception as e:
            logger.error(f"Diagram update failed: {e}")
            return {
                'error': f'Diagram update failed: {str(e)}'
            }

    def _apply_change(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Apply a single change to the UML model."""
        change_type = change.get('type')

        if change_type == 'add_class':
            self._add_class(uml_model, change)
        elif change_type == 'remove_class':
            self._remove_class(uml_model, change)
        elif change_type == 'modify_class':
            self._modify_class(uml_model, change)
        elif change_type == 'add_relationship':
            self._add_relationship(uml_model, change)
        elif change_type == 'remove_relationship':
            self._remove_relationship(uml_model, change)
        elif change_type == 'modify_relationship':
            self._modify_relationship(uml_model, change)
        else:
            logger.warning(f"Unknown change type: {change_type}")

    def _add_class(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Add a new class to the model."""
        from ..models.uml_model import UMLClass, Attribute, Method, Point

        class_data = change.get('class', {})
        new_class = UMLClass(
            name=class_data.get('name', 'NewClass'),
            position=Point(
                x=class_data.get('position', {}).get('x', 0),
                y=class_data.get('position', {}).get('y', 0)
            )
        )

        # Add attributes
        for attr_data in class_data.get('attributes', []):
            attr = Attribute(
                name=attr_data.get('name', 'attribute'),
                type=attr_data.get('type', 'String'),
                visibility=attr_data.get('visibility', '+')
            )
            new_class.attributes.append(attr)

        # Add methods
        for method_data in class_data.get('methods', []):
            method = Method(
                name=method_data.get('name', 'method'),
                parameters=method_data.get('parameters', []),
                return_type=method_data.get('return_type', 'void'),
                visibility=method_data.get('visibility', '+')
            )
            new_class.methods.append(method)

        uml_model.add_class(new_class)

    def _remove_class(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Remove a class from the model."""
        class_name = change.get('class_name')
        if class_name:
            uml_model.remove_class(class_name)

    def _modify_class(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Modify an existing class."""
        class_name = change.get('class_name')
        modifications = change.get('modifications', {})

        cls = uml_model.find_class(class_name)
        if cls:
            if 'name' in modifications:
                cls.name = modifications['name']

            if 'add_attributes' in modifications:
                for attr_data in modifications['add_attributes']:
                    from ..models.uml_model import Attribute
                    attr = Attribute(
                        name=attr_data.get('name', 'attribute'),
                        type=attr_data.get('type', 'String'),
                        visibility=attr_data.get('visibility', '+')
                    )
                    cls.attributes.append(attr)

            if 'add_methods' in modifications:
                for method_data in modifications['add_methods']:
                    from ..models.uml_model import Method
                    method = Method(
                        name=method_data.get('name', 'method'),
                        parameters=method_data.get('parameters', []),
                        return_type=method_data.get('return_type', 'void'),
                        visibility=method_data.get('visibility', '+')
                    )
                    cls.methods.append(method)

    def _add_relationship(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Add a new relationship to the model."""
        from ..models.uml_model import UMLRelationship, RelationshipType

        rel_data = change.get('relationship', {})
        relationship = UMLRelationship(
            source=rel_data.get('source', ''),
            target=rel_data.get('target', ''),
            type=RelationshipType(rel_data.get('type', 'association')),
            multiplicity_source=rel_data.get('multiplicity_source', '1'),
            multiplicity_target=rel_data.get('multiplicity_target', '1'),
            label=rel_data.get('label', '')
        )
        uml_model.add_relationship(relationship)

    def _remove_relationship(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Remove a relationship from the model."""
        source = change.get('source')
        target = change.get('target')
        if source and target:
            uml_model.remove_relationship(source, target)

    def _modify_relationship(self, uml_model: UMLModel, change: Dict[str, Any]):
        """Modify an existing relationship."""
        source = change.get('source')
        target = change.get('target')
        modifications = change.get('modifications', {})

        rel = uml_model.find_relationship(source, target)
        if rel:
            if 'type' in modifications:
                from ..models.uml_model import RelationshipType
                rel.type = RelationshipType(modifications['type'])
            if 'multiplicity_source' in modifications:
                rel.multiplicity_source = modifications['multiplicity_source']
            if 'multiplicity_target' in modifications:
                rel.multiplicity_target = modifications['multiplicity_target']
            if 'label' in modifications:
                rel.label = modifications['label']

    def get_diagram_statistics(self, uml_model: UMLModel) -> Dict[str, Any]:
        """Get statistics about the UML diagram."""
        stats = {
            'classes': {
                'total': len(uml_model.classes),
                'with_attributes': len([c for c in uml_model.classes if c.attributes]),
                'with_methods': len([c for c in uml_model.classes if c.methods])
            },
            'relationships': {
                'total': len(uml_model.relationships),
                'by_type': {}
            },
            'complexity': 'simple'
        }

        # Count relationships by type
        for rel in uml_model.relationships:
            rel_type = rel.type.value
            stats['relationships']['by_type'][rel_type] = stats['relationships']['by_type'].get(rel_type, 0) + 1

        # Determine complexity
        if len(uml_model.classes) > 10 or len(uml_model.relationships) > 15:
            stats['complexity'] = 'complex'
        elif len(uml_model.classes) > 5 or len(uml_model.relationships) > 7:
            stats['complexity'] = 'medium'

        return stats