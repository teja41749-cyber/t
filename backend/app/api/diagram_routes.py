from flask import Blueprint, request, jsonify
import logging
import json
from ..services.diagram_generator import DiagramGenerator
from ..models.uml_model import UMLModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

diagram_bp = Blueprint('diagram', __name__)

# Initialize services
diagram_generator = DiagramGenerator()

@diagram_bp.route('/update', methods=['POST'])
@limiter.limit("20 per minute")
def update_diagram():
    """
    Update diagram based on user modifications.

    Request body:
    {
        "uml_model": {...},
        "changes": [
            {
                "type": "add_class|remove_class|modify_class|add_relationship|remove_relationship|modify_relationship",
                "data": {...}
            }
        ]
    }

    Response:
    {
        "uml_model": {...},
        "mermaid_code": "...",
        "changes_applied": [...]
    }
    """
    try:
        data = request.get_json()
        uml_model_data = data.get('uml_model')
        changes = data.get('changes', [])

        if not uml_model_data:
            return jsonify({
                'error': 'UML model is required',
                'code': 'MISSING_MODEL'
            }), 400

        logger.info(f"Updating diagram with {len(changes)} changes")

        # Reconstruct UML model from data
        uml_model = UMLModel.from_dict(uml_model_data)

        # Apply changes
        updated_diagram = diagram_generator.update_diagram(uml_model, changes)

        if 'error' in updated_diagram:
            return jsonify(updated_diagram), 400

        # Get updated statistics
        stats = diagram_generator.get_diagram_statistics(uml_model)

        response_data = {
            'uml_model': uml_model.to_dict(),
            'mermaid_code': updated_diagram['code'],
            'changes_applied': changes,
            'metadata': {
                'statistics': stats,
                'validation': updated_diagram.get('validation', {})
            }
        }

        logger.info("Diagram updated successfully")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Diagram update failed: {e}")
        return jsonify({
            'error': 'Diagram update failed',
            'details': str(e),
            'code': 'UPDATE_ERROR'
        }), 500

@diagram_bp.route('/export', methods=['POST'])
@limiter.limit("10 per minute")
def export_diagram():
    """
    Export diagram in various formats.

    Request body:
    {
        "uml_model": {...},
        "format": "mermaid|svg|png|json"
    }

    Response:
    {
        "format": "...",
        "data": "...",
        "filename": "..."
    }
    """
    try:
        data = request.get_json()
        uml_model_data = data.get('uml_model')
        format_type = data.get('format', 'mermaid').lower()

        if not uml_model_data:
            return jsonify({
                'error': 'UML model is required',
                'code': 'MISSING_MODEL'
            }), 400

        if format_type not in ['mermaid', 'json']:
            return jsonify({
                'error': f'Format {format_type} not supported',
                'supported_formats': ['mermaid', 'json'],
                'code': 'UNSUPPORTED_FORMAT'
            }), 400

        # Reconstruct UML model
        uml_model = UMLModel.from_dict(uml_model_data)

        # Generate diagram
        diagram_result = diagram_generator.generate_diagram(uml_model, format_type)

        if 'error' in diagram_result:
            return jsonify(diagram_result), 400

        # Prepare export data
        if format_type == 'mermaid':
            export_data = diagram_result['code']
            filename = 'uml_diagram.mmd'
        elif format_type == 'json':
            export_data = json.dumps(uml_model.to_dict(), indent=2)
            filename = 'uml_model.json'

        response_data = {
            'format': format_type,
            'data': export_data,
            'filename': filename,
            'metadata': {
                'class_count': len(uml_model.classes),
                'relationship_count': len(uml_model.relationships),
                'exported_at': str(diagram_generator.mermaid_converter.__class__.__name__)
            }
        }

        logger.info(f"Diagram exported in {format_type} format")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Diagram export failed: {e}")
        return jsonify({
            'error': 'Diagram export failed',
            'details': str(e),
            'code': 'EXPORT_ERROR'
        }), 500

@diagram_bp.route('/validate', methods=['POST'])
@limiter.limit("15 per minute")
def validate_diagram():
    """
    Validate UML diagram structure and syntax.

    Request body:
    {
        "uml_model": {...}
    }

    Response:
    {
        "is_valid": true/false,
        "issues": [...],
        "suggestions": [...]
    }
    """
    try:
        data = request.get_json()
        uml_model_data = data.get('uml_model')

        if not uml_model_data:
            return jsonify({
                'error': 'UML model is required',
                'code': 'MISSING_MODEL'
            }), 400

        # Reconstruct UML model
        uml_model = UMLModel.from_dict(uml_model_data)

        validation_result = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'warnings': []
        }

        # Validate classes
        class_names = [cls.name.lower() for cls in uml_model.classes]
        if len(class_names) != len(set(class_names)):
            validation_result['is_valid'] = False
            validation_result['issues'].append({
                'type': 'duplicate_class',
                'message': 'Duplicate class names found',
                'severity': 'error'
            })

        # Validate relationships
        for rel in uml_model.relationships:
            source_class = uml_model.find_class(rel.source)
            target_class = uml_model.find_class(rel.target)

            if not source_class:
                validation_result['is_valid'] = False
                validation_result['issues'].append({
                    'type': 'missing_class',
                    'message': f'Relationship source class "{rel.source}" not found',
                    'severity': 'error',
                    'relationship': f'{rel.source} -> {rel.target}'
                })

            if not target_class:
                validation_result['is_valid'] = False
                validation_result['issues'].append({
                    'type': 'missing_class',
                    'message': f'Relationship target class "{rel.target}" not found',
                    'severity': 'error',
                    'relationship': f'{rel.source} -> {rel.target}'
                })

            # Check for self-referencing relationships
            if rel.source.lower() == rel.target.lower():
                validation_result['warnings'].append({
                    'type': 'self_reference',
                    'message': f'Self-referencing relationship in class "{rel.source}"',
                    'severity': 'warning'
                })

        # Generate Mermaid and validate syntax
        diagram_result = diagram_generator.generate_diagram(uml_model, "mermaid")
        mermaid_validation = diagram_result.get('validation', {})

        if not mermaid_validation.get('is_valid', True):
            validation_result['issues'].extend([
                {
                    'type': 'syntax',
                    'message': error,
                    'severity': 'error'
                } for error in mermaid_validation.get('errors', [])
            ])

        validation_result['warnings'].extend([
            {
                'type': 'syntax',
                'message': warning,
                'severity': 'warning'
            } for warning in mermaid_validation.get('warnings', [])
        ])

        # Provide suggestions
        if len(uml_model.classes) == 0:
            validation_result['suggestions'].append('Consider adding at least one class to create a meaningful diagram')

        if len(uml_model.relationships) == 0 and len(uml_model.classes) > 1:
            validation_result['suggestions'].append('Consider adding relationships between classes to show system structure')

        # Get diagram statistics
        stats = diagram_generator.get_diagram_statistics(uml_model)
        validation_result['statistics'] = stats

        return jsonify(validation_result)

    except Exception as e:
        logger.error(f"Diagram validation failed: {e}")
        return jsonify({
            'error': 'Diagram validation failed',
            'details': str(e),
            'code': 'VALIDATION_ERROR'
        }), 500

@diagram_bp.route('/statistics', methods=['POST'])
@limiter.limit("15 per minute")
def get_statistics():
    """
    Get detailed statistics about the UML diagram.

    Request body:
    {
        "uml_model": {...}
    }

    Response:
    {
        "statistics": {...},
        "complexity": "...",
        "recommendations": [...]
    }
    """
    try:
        data = request.get_json()
        uml_model_data = data.get('uml_model')

        if not uml_model_data:
            return jsonify({
                'error': 'UML model is required',
                'code': 'MISSING_MODEL'
            }), 400

        # Reconstruct UML model
        uml_model = UMLModel.from_dict(uml_model_data)

        # Get statistics
        stats = diagram_generator.get_diagram_statistics(uml_model)

        # Add detailed statistics
        detailed_stats = {
            **stats,
            'attributes': {
                'total': sum(len(cls.attributes) for cls in uml_model.classes),
                'types': {}
            },
            'methods': {
                'total': sum(len(cls.methods) for cls in uml_model.classes),
                'return_types': {}
            }
        }

        # Count attribute types
        for cls in uml_model.classes:
            for attr in cls.attributes:
                attr_type = attr.type
                detailed_stats['attributes']['types'][attr_type] = detailed_stats['attributes']['types'].get(attr_type, 0) + 1

        # Count method return types
        for cls in uml_model.classes:
            for method in cls.methods:
                return_type = method.return_type
                detailed_stats['methods']['return_types'][return_type] = detailed_stats['methods']['return_types'].get(return_type, 0) + 1

        # Generate recommendations
        recommendations = []

        if detailed_stats['classes']['total'] == 0:
            recommendations.append('Add at least one class to start building your UML diagram')
        elif detailed_stats['classes']['total'] == 1:
            recommendations.append('Consider adding more classes to show relationships and system structure')
        elif detailed_stats['classes']['total'] > 15:
            recommendations.append('Large number of classes detected - consider breaking into multiple diagrams')

        if detailed_stats['relationships']['total'] == 0 and detailed_stats['classes']['total'] > 1:
            recommendations.append('Add relationships between classes to show how they interact')

        if detailed_stats['classes']['with_attributes'] == 0:
            recommendations.append('Add attributes to classes to define their properties and data')

        if detailed_stats['classes']['with_methods'] == 0:
            recommendations.append('Add methods to classes to define their behavior and operations')

        response_data = {
            'statistics': detailed_stats,
            'complexity': stats['complexity'],
            'recommendations': recommendations,
            'quality_score': _calculate_quality_score(detailed_stats)
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Statistics generation failed: {e}")
        return jsonify({
            'error': 'Statistics generation failed',
            'details': str(e),
            'code': 'STATISTICS_ERROR'
        }), 500

def _calculate_quality_score(stats: dict) -> float:
    """Calculate a quality score for the UML diagram."""
    score = 0.0

    # Base score for having classes
    if stats['classes']['total'] > 0:
        score += 20

    # Points for attributes
    if stats['attributes']['total'] > 0:
        score += 20

    # Points for methods
    if stats['methods']['total'] > 0:
        score += 20

    # Points for relationships
    if stats['relationships']['total'] > 0:
        score += 20

    # Bonus for having all three elements
    if (stats['classes']['total'] > 0 and
        stats['attributes']['total'] > 0 and
        stats['relationships']['total'] > 0):
        score += 20

    return min(score, 100.0)