from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import time
from ..services.nlp_processor import NLPProcessor
from ..services.diagram_generator import DiagramGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nlp_bp = Blueprint('nlp', __name__)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

# Initialize services
nlp_processor = NLPProcessor()
diagram_generator = DiagramGenerator()

@nlp_bp.route('/extract', methods=['POST'])
@limiter.limit("10 per minute")
def extract_uml():
    """
    Extract UML model from requirement text.

    Request body:
    {
        "text": "User requirements text here..."
    }

    Response:
    {
        "uml_model": {...},
        "mermaid_code": "...",
        "metadata": {...}
    }
    """
    try:
        start_time = time.time()
        data = request.get_json()
        text = data.get('text', '').strip()

        # Input validation
        if not text:
            return jsonify({
                'error': 'Text is required',
                'code': 'MISSING_TEXT'
            }), 400

        if len(text) < 50:
            return jsonify({
                'error': 'Text too short (minimum 50 characters required)',
                'code': 'TEXT_TOO_SHORT',
                'received_length': len(text),
                'minimum_length': 50
            }), 400

        if len(text) > 10000:
            return jsonify({
                'error': 'Text too long (maximum 10000 characters allowed)',
                'code': 'TEXT_TOO_LONG',
                'received_length': len(text),
                'maximum_length': 10000
            }), 400

        logger.info(f"Processing text of length {len(text)} characters")

        # Process requirements through NLP pipeline
        uml_model = nlp_processor.process_requirements(text)

        # Generate diagram
        diagram_result = diagram_generator.generate_diagram(uml_model, "mermaid")

        # Get statistics
        stats = diagram_generator.get_diagram_statistics(uml_model)

        processing_time = time.time() - start_time

        response_data = {
            'uml_model': uml_model.to_dict(),
            'mermaid_code': diagram_result['code'],
            'metadata': {
                'processing_time': round(processing_time, 2),
                'text_length': len(text),
                'statistics': stats,
                'validation': diagram_result.get('validation', {}),
                'export_formats': diagram_result.get('export_formats', {})
            }
        }

        logger.info(f"Successfully processed text in {processing_time:.2f}s")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"NLP processing failed: {e}")
        return jsonify({
            'error': 'NLP processing failed',
            'details': str(e),
            'code': 'PROCESSING_ERROR'
        }), 500

@nlp_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for NLP services."""
    try:
        # Check if services are available
        bert_available = nlp_processor.bert_extractor.ner_pipeline is not None
        spacy_available = nlp_processor.spacy_analyzer.nlp is not None

        health_status = {
            'status': 'healthy',
            'services': {
                'bert_extractor': 'available' if bert_available else 'unavailable',
                'spacy_analyzer': 'available' if spacy_available else 'unavailable',
                'text_preprocessor': 'available',
                'diagram_generator': 'available'
            },
            'version': '1.0.0'
        }

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@nlp_bp.route('/validate', methods=['POST'])
def validate_requirements():
    """
    Validate requirement text before processing.

    Request body:
    {
        "text": "Requirements text to validate"
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
        text = data.get('text', '').strip()

        validation_result = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'statistics': {
                'character_count': len(text),
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()])
            }
        }

        # Check length requirements
        if len(text) < 50:
            validation_result['is_valid'] = False
            validation_result['issues'].append({
                'type': 'length',
                'message': 'Text is too short for meaningful UML extraction',
                'severity': 'error'
            })

        if len(text) > 10000:
            validation_result['is_valid'] = False
            validation_result['issues'].append({
                'type': 'length',
                'message': 'Text exceeds maximum length limit',
                'severity': 'error'
            })

        # Check for meaningful content
        meaningful_indicators = ['class', 'user', 'system', 'has', 'contains', 'manages', 'interface']
        has_meaningful_content = any(indicator in text.lower() for indicator in meaningful_indicators)

        if not has_meaningful_content:
            validation_result['issues'].append({
                'type': 'content',
                'message': 'Text may not contain sufficient software requirements for UML extraction',
                'severity': 'warning'
            })
            validation_result['suggestions'].append('Consider adding more specific requirements about classes, relationships, or system components')

        # Check for common patterns
        if 'user' in text.lower() and 'login' in text.lower():
            validation_result['suggestions'].append('Detected user authentication patterns - consider User, Account, or Login classes')

        if 'database' in text.lower() or 'data' in text.lower():
            validation_result['suggestions'].append('Detected data-related requirements - consider DataModel or Repository classes')

        return jsonify(validation_result)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({
            'error': 'Validation failed',
            'details': str(e)
        }), 500

@nlp_bp.route('/models/preload', methods=['POST'])
def preload_models():
    """
    Preload NLP models to reduce first-request latency.

    Response:
    {
        "status": "success",
        "models_loaded": [...]
    }
    """
    try:
        logger.info("Preloading NLP models")

        # Force model loading
        if nlp_processor.bert_extractor.ner_pipeline is None:
            nlp_processor.bert_extractor._load_model()

        if nlp_processor.spacy_analyzer.nlp is None:
            nlp_processor.spacy_analyzer._load_model()

        models_loaded = []
        if nlp_processor.bert_extractor.ner_pipeline:
            models_loaded.append('bert_extractor')
        if nlp_processor.spacy_analyzer.nlp:
            models_loaded.append('spacy_analyzer')

        response_data = {
            'status': 'success',
            'models_loaded': models_loaded,
            'message': f'Preloaded {len(models_loaded)} models'
        }

        logger.info(f"Successfully preloaded {len(models_loaded)} models")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Model preloading failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Error handlers
@nlp_bp.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'code': 'RATE_LIMIT_EXCEEDED'
    }), 429

@nlp_bp.errorhandler(400)
def bad_request_handler(e):
    """Handle bad request errors."""
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request format or data',
        'code': 'BAD_REQUEST'
    }), 400

@nlp_bp.errorhandler(500)
def internal_error_handler(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'code': 'INTERNAL_ERROR'
    }), 500