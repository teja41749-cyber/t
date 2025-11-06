from typing import List, Dict, Any
import logging
from ..models.uml_model import UMLModel, UMLClass, UMLRelationship, Attribute, Method, RelationshipType
from ..models.nlp_result import NLPResult
from ..utils.text_preprocessing import TextPreprocessor
from .bert_extractor import BERTExtractor
from .spacy_analyzer import SpaCyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processing pipeline."""
        self.text_preprocessor = TextPreprocessor()
        self.bert_extractor = BERTExtractor()
        self.spacy_analyzer = SpaCyAnalyzer()
        self.processing_timeout = 30  # seconds

    def process_requirements(self, text: str) -> UMLModel:
        """
        Process requirement text through the complete NLP pipeline.

        Args:
            text: Raw requirement text

        Returns:
            UMLModel with extracted classes, attributes, and relationships
        """
        try:
            logger.info("Starting NLP processing pipeline")
            nlp_result = NLPResult()

            # Stage 1: Text preprocessing
            logger.info("Stage 1: Text preprocessing")
            cleaned_text = self.text_preprocessor.preprocess_text(text)
            nlp_result.processed_text = cleaned_text
            nlp_result.metadata['original_length'] = len(text)
            nlp_result.metadata['processed_length'] = len(cleaned_text)

            # Handle long texts by chunking
            if len(cleaned_text) > 400:
                chunks = self.text_preprocessor.chunk_text(cleaned_text)
                nlp_result.metadata['chunks'] = len(chunks)
                logger.info(f"Text split into {len(chunks)} chunks for processing")
            else:
                chunks = [cleaned_text]
                nlp_result.metadata['chunks'] = 1

            # Stage 2: Entity extraction (BERT)
            logger.info("Stage 2: Entity extraction")
            all_entities = []
            for chunk in chunks:
                entities = self.bert_extractor.extract_entities(chunk)
                all_entities.extend(entities)

            nlp_result.entities = self._merge_duplicate_entities(all_entities)
            logger.info(f"Extracted {len(nlp_result.entities)} entities")

            # Stage 3: Relationship analysis (spaCy)
            logger.info("Stage 3: Relationship analysis")
            all_relationships = []
            for chunk in chunks:
                chunk_entities = [e for e in nlp_result.entities if chunk.find(e.text) != -1]
                relationships = self.spacy_analyzer.extract_relationships(chunk, chunk_entities)
                all_relationships.extend(relationships)

            nlp_result.relationships = all_relationships
            logger.info(f"Extracted {len(nlp_result.relationships)} relationships")

            # Stage 4: UML model construction
            logger.info("Stage 4: UML model construction")
            uml_model = self.build_uml_model(nlp_result)

            logger.info("NLP processing pipeline completed successfully")
            return uml_model

        except Exception as e:
            logger.error(f"NLP processing failed: {e}")
            raise Exception(f"NLP processing failed: {str(e)}")

    def _merge_duplicate_entities(self, entities: List) -> List:
        """Merge duplicate entities keeping the one with highest confidence."""
        entity_map = {}

        for entity in entities:
            key = entity.text.lower()
            if key not in entity_map:
                entity_map[key] = entity
            else:
                # Keep the entity with higher confidence
                if entity.confidence > entity_map[key].confidence:
                    entity_map[key] = entity

        return list(entity_map.values())

    def build_uml_model(self, nlp_result: NLPResult) -> UMLModel:
        """
        Convert NLP results to UML model structure.

        Args:
            nlp_result: Results from NLP processing

        Returns:
            Structured UML model
        """
        uml_model = UMLModel()

        # Build classes from entities
        classes = self._build_classes_from_entities(nlp_result.get_classes())
        for cls in classes:
            uml_model.add_class(cls)

        # Add attributes to classes
        self._add_attributes_to_classes(uml_model, nlp_result.get_attributes())

        # Add methods to classes
        self._add_methods_to_classes(uml_model, nlp_result.get_methods())

        # Build relationships
        relationships = self._build_relationships(nlp_result.relationships, uml_model)
        for rel in relationships:
            uml_model.add_relationship(rel)

        # Post-process model for quality improvements
        self._post_process_uml_model(uml_model)

        return uml_model

    def _build_classes_from_entities(self, class_entities: List) -> List[UMLClass]:
        """Build UML classes from extracted entities."""
        classes = []

        for entity in class_entities:
            # Filter out non-class entities
            if entity.label == 'CLASS':
                uml_class = UMLClass(
                    name=entity.text,
                    confidence=entity.confidence
                )
                classes.append(uml_class)

        # Sort by confidence
        classes.sort(key=lambda c: c.confidence, reverse=True)
        return classes

    def _add_attributes_to_classes(self, uml_model: UMLModel, attribute_entities: List):
        """Add attributes to appropriate classes."""
        for attr_entity in attribute_entities:
            # Find the class this attribute belongs to
            target_class = None

            # First check if entity has explicit belongs_to
            if attr_entity.belongs_to:
                target_class = uml_model.find_class(attr_entity.belongs_to)

            # If not found, try to infer from proximity or naming
            if not target_class:
                target_class = self._infer_attribute_class(attr_entity, uml_model)

            if target_class:
                attribute = Attribute(
                    name=attr_entity.text,
                    type=self._infer_attribute_type(attr_entity.text),
                    confidence=attr_entity.confidence
                )
                target_class.attributes.append(attribute)

    def _add_methods_to_classes(self, uml_model: UMLModel, method_entities: List):
        """Add methods to appropriate classes."""
        for method_entity in method_entities:
            target_class = self._infer_method_class(method_entity, uml_model)

            if target_class:
                method = Method(
                    name=method_entity.text,
                    parameters=self._infer_method_parameters(method_entity.text),
                    return_type=self._infer_method_return_type(method_entity.text),
                    confidence=method_entity.confidence
                )
                target_class.methods.append(method)

    def _build_relationships(self, nlp_relationships: List, uml_model: UMLModel) -> List[UMLRelationship]:
        """Build UML relationships from NLP results."""
        relationships = []

        for nlp_rel in nlp_relationships:
            # Find the corresponding classes
            source_class = uml_model.find_class(nlp_rel.source)
            target_class = uml_model.find_class(nlp_rel.target)

            if source_class and target_class:
                # Map relationship type
                rel_type = self._map_relationship_type(nlp_rel.relationship_type)

                uml_rel = UMLRelationship(
                    source=source_class.name,
                    target=target_class.name,
                    type=rel_type,
                    multiplicity_source=self._infer_multiplicity(nlp_rel.context, 'source'),
                    multiplicity_target=self._infer_multiplicity(nlp_rel.context, 'target'),
                    label=nlp_rel.context[:50] + '...' if len(nlp_rel.context) > 50 else nlp_rel.context,
                    confidence=nlp_rel.confidence
                )
                relationships.append(uml_rel)

        return relationships

    def _infer_attribute_class(self, attr_entity, uml_model: UMLModel):
        """Infer which class an attribute belongs to."""
        # Simple heuristic: check if attribute name contains class name
        for cls in uml_model.classes:
            if cls.name.lower() in attr_entity.text.lower():
                return cls

        # If no clear match, return the class with highest confidence
        if uml_model.classes:
            return max(uml_model.classes, key=lambda c: c.confidence)

        return None

    def _infer_method_class(self, method_entity, uml_model: UMLModel):
        """Infer which class a method belongs to."""
        # Similar to attribute inference
        for cls in uml_model.classes:
            if cls.name.lower() in method_entity.text.lower():
                return cls

        # Common CRUD operations usually belong to the most relevant class
        if uml_model.classes:
            return max(uml_model.classes, key=lambda c: c.confidence)

        return None

    def _infer_attribute_type(self, attr_name: str) -> str:
        """Infer attribute type from name."""
        attr_name_lower = attr_name.lower()

        # Common type patterns
        if any(keyword in attr_name_lower for keyword in ['id', 'code', 'number']):
            return 'Integer'
        elif any(keyword in attr_name_lower for keyword in ['price', 'amount', 'balance', 'rate']):
            return 'Float'
        elif any(keyword in attr_name_lower for keyword in ['date', 'time', 'created', 'updated']):
            return 'DateTime'
        elif any(keyword in attr_name_lower for keyword in ['is', 'has', 'can', 'active', 'enabled']):
            return 'Boolean'
        elif any(keyword in attr_name_lower for keyword in ['email', 'name', 'description', 'title']):
            return 'String'
        else:
            return 'String'  # Default type

    def _infer_method_parameters(self, method_name: str) -> List[str]:
        """Infer method parameters from name."""
        method_name_lower = method_name.lower()

        # Common method patterns
        if 'get' in method_name_lower:
            return []
        elif 'set' in method_name_lower or 'update' in method_name_lower:
            return ['value']
        elif 'create' in method_name_lower:
            return ['data']
        elif 'delete' in method_name_lower:
            return ['id']
        else:
            return []

    def _infer_method_return_type(self, method_name: str) -> str:
        """Infer method return type from name."""
        method_name_lower = method_name.lower()

        if any(keyword in method_name_lower for keyword in ['get', 'find', 'list', 'show']):
            return 'Object'
        elif any(keyword in method_name_lower for keyword in ['is', 'has', 'can', 'exists']):
            return 'Boolean'
        elif any(keyword in method_name_lower for keyword in ['count', 'size']):
            return 'Integer'
        elif any(keyword in method_name_lower for keyword in ['set', 'update', 'delete', 'save']):
            return 'void'
        else:
            return 'void'

    def _map_relationship_type(self, nlp_rel_type: str) -> RelationshipType:
        """Map NLP relationship type to UML relationship type."""
        type_mapping = {
            'composition': RelationshipType.COMPOSITION,
            'association': RelationshipType.ASSOCIATION,
            'inheritance': RelationshipType.INHERITANCE,
            'aggregation': RelationshipType.AGGREGATION
        }

        return type_mapping.get(nlp_rel_type, RelationshipType.ASSOCIATION)

    def _infer_multiplicity(self, context: str, side: str) -> str:
        """Infer multiplicity from context."""
        context_lower = context.lower()

        # Look for multiplicity indicators
        if any(indicator in context_lower for indicator in ['many', 'multiple', 'various', 'list']):
            return '1..*'
        elif any(indicator in context_lower for indicator in ['optional', 'may have', 'can have']):
            return '0..1'
        elif any(indicator in context_lower for indicator in ['collection', 'group', 'set']):
            return '1..*'
        else:
            return '1'

    def _post_process_uml_model(self, uml_model: UMLModel):
        """Post-process the UML model for quality improvements."""
        # Remove duplicate attributes within classes
        for cls in uml_model.classes:
            seen_attrs = set()
            unique_attrs = []
            for attr in cls.attributes:
                if attr.name.lower() not in seen_attrs:
                    seen_attrs.add(attr.name.lower())
                    unique_attrs.append(attr)
            cls.attributes = unique_attrs

        # Remove duplicate methods within classes
        for cls in uml_model.classes:
            seen_methods = set()
            unique_methods = []
            for method in cls.methods:
                if method.name.lower() not in seen_methods:
                    seen_methods.add(method.name.lower())
                    unique_methods.append(method)
            cls.methods = unique_methods

        # Remove self-referencing relationships
        uml_model.relationships = [
            rel for rel in uml_model.relationships
            if rel.source.lower() != rel.target.lower()
        ]

        # Sort classes by name for consistency
        uml_model.classes.sort(key=lambda c: c.name.lower())
        uml_model.relationships.sort(key=lambda r: (r.source.lower(), r.target.lower()))