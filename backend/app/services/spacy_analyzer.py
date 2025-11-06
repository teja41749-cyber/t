import spacy
from typing import List, Dict, Any, Tuple
import logging
import re
from ..models.nlp_result import NLPRelationship, NLPEntity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpaCyAnalyzer:
    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Initialize spaCy analyzer for relationship extraction.

        Args:
            model_name: spaCy model name
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()

    def _load_model(self):
        """Load spaCy model."""
        try:
            logger.info(f"Loading spaCy model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning(f"spaCy model {self.model_name} not found, using basic pattern matching")
            self.nlp = None

    def extract_relationships(self, text: str, entities: List[NLPEntity] = None) -> List[NLPRelationship]:
        """
        Extract relationships between entities from text.

        Args:
            text: Input requirement text
            entities: List of previously identified entities

        Returns:
            List of extracted relationships
        """
        if not self.nlp:
            return self._pattern_based_extraction(text, entities)

        relationships = []

        try:
            doc = self.nlp(text)
            entity_names = [e.text.lower() for e in entities] if entities else []

            # Extract relationships using dependency parsing
            for sent in doc.sents:
                sent_relationships = self._extract_sentence_relationships(sent, entity_names)
                relationships.extend(sent_relationships)

            # Post-process relationships
            relationships = self._post_process_relationships(relationships, text)

        except Exception as e:
            logger.error(f"spaCy analysis failed: {e}")
            return self._pattern_based_extraction(text, entities)

        return relationships

    def _extract_sentence_relationships(self, sent, entity_names: List[str]) -> List[NLPRelationship]:
        """Extract relationships from a single sentence."""
        relationships = []

        # Find subjects and objects
        for token in sent:
            if token.dep_ in ['nsubj', 'nsubjpass', 'dobj', 'pobj', 'agent']:
                subject = self._find_entity_name(token.head, entity_names)
                object = self._find_entity_name(token, entity_names)

                if subject and object and subject != object:
                    rel_type = self._determine_relationship_type(token, token.head)
                    context = sent.text

                    relationship = NLPRelationship(
                        source=subject,
                        target=object,
                        relationship_type=rel_type,
                        confidence=0.8,
                        context=context
                    )
                    relationships.append(relationship)

        return relationships

    def _find_entity_name(self, token, entity_names: List[str]) -> str:
        """Find the best matching entity name for a token."""
        # Check the token itself
        if token.text.lower() in entity_names:
            return token.text

        # Check the token's head
        if token.head.text.lower() in entity_names:
            return token.head.text

        # Check children
        for child in token.children:
            if child.text.lower() in entity_names:
                return child.text

        # Fuzzy matching for compound nouns
        token_text = token.text.lower()
        for entity_name in entity_names:
            if entity_name in token_text or token_text in entity_name:
                # Find the original entity name (not the lowercased version)
                for entity in self._get_original_entities():
                    if entity.text.lower() == entity_name:
                        return entity.text

        return None

    def _get_original_entities(self) -> List[NLPEntity]:
        """Get original entities for name resolution."""
        # This would typically be passed in or stored as a class variable
        # For now, return empty list
        return []

    def _determine_relationship_type(self, token, head) -> str:
        """Determine relationship type based on dependency and POS tags."""
        # Relationship indicators
        composition_indicators = ['contain', 'have', 'own', 'manage', 'control']
        association_indicators = ['use', 'reference', 'connect', 'link', 'access']
        inheritance_indicators = ['extend', 'inherit', 'be', 'become']
        aggregation_indicators = ['collection', 'group', 'set', 'list']

        token_text = token.text.lower()
        head_text = head.text.lower()

        # Check for composition
        if any(indicator in token_text or indicator in head_text for indicator in composition_indicators):
            return 'composition'

        # Check for inheritance
        if any(indicator in token_text or indicator in head_text for indicator in inheritance_indicators):
            return 'inheritance'

        # Check for aggregation
        if any(indicator in token_text or indicator in head_text for indicator in aggregation_indicators):
            return 'aggregation'

        # Default to association
        return 'association'

    def _pattern_based_extraction(self, text: str, entities: List[NLPEntity] = None) -> List[NLPRelationship]:
        """Fallback pattern-based relationship extraction."""
        if not entities:
            return []

        relationships = []
        entity_names = [e.text.lower() for e in entities]

        # Define relationship patterns
        patterns = [
            # Composition patterns
            (r'(\w+)\s+(contains?|has|have|owns?|manages?)\s+(\w+)', 'composition'),
            (r'(\w+)\s+is\s+part\s+of\s+(\w+)', 'composition'),
            (r'(\w+)\'s?\s+(\w+)', 'composition'),

            # Association patterns
            (r'(\w+)\s+(uses?|references?|connects?\s+to|links?\s+to)\s+(\w+)', 'association'),
            (r'(\w+)\s+(talks?\s+to|communicates?\s+with)\s+(\w+)', 'association'),

            # Inheritance patterns
            (r'(\w+)\s+(extends?|inherits?\s+from|is\s+a\s+type\s+of)\s+(\w+)', 'inheritance'),
            (r'(\w+)\s+is\s+a\s+(\w+)', 'inheritance'),

            # Aggregation patterns
            (r'(\w+)\s+(has\s+multiple|collection\s+of|group\s+of)\s+(\w+)', 'aggregation'),
            (r'(many|multiple|various)\s+(\w+)\s+(belong\s+to|are\s+in)\s+(\w+)', 'aggregation')
        ]

        for pattern, rel_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    # Determine source and target based on pattern
                    if len(groups) == 3 and groups[1].lower() in ['contains', 'has', 'have', 'owns', 'manages', 'uses', 'references', 'extends', 'inherits', 'connects', 'links']:
                        source, target = groups[0], groups[2]
                    elif len(groups) == 3 and groups[1].lower() in ['is', 'are']:
                        source, target = groups[2], groups[0]
                    elif len(groups) == 2:
                        source, target = groups[0], groups[1]
                    else:
                        continue

                    # Check if both entities are in our entity list
                    if (source.lower() in entity_names and target.lower() in entity_names):
                        # Extract multiplicity
                        multiplicity = self._extract_multiplicity(match.group())

                        relationship = NLPRelationship(
                            source=source,
                            target=target,
                            relationship_type=rel_type,
                            confidence=0.7,
                            context=match.group()
                        )
                        relationships.append(relationship)

        return relationships

    def _extract_multiplicity(self, context: str) -> Tuple[str, str]:
        """Extract multiplicity indicators from context."""
        multiplicity_patterns = {
            'one': '1',
            'many': '1..*',
            'multiple': '1..*',
            'optional': '0..1',
            'zero or more': '0..*',
            'one or more': '1..*',
            'exactly one': '1',
            'two': '2',
            'three': '3'
        }

        source_mult = '1'
        target_mult = '1'

        for pattern, mult in multiplicity_patterns.items():
            if pattern in context.lower():
                if context.lower().index(pattern) < len(context) / 2:
                    source_mult = mult
                else:
                    target_mult = mult

        return source_mult, target_mult

    def _post_process_relationships(self, relationships: List[NLPRelationship], text: str) -> List[NLPRelationship]:
        """Post-process relationships to remove duplicates and improve accuracy."""
        # Remove duplicate relationships
        seen_relationships = set()
        unique_relationships = []

        for rel in relationships:
            key = (rel.source.lower(), rel.target.lower(), rel.relationship_type)
            if key not in seen_relationships:
                seen_relationships.add(key)
                unique_relationships.append(rel)

        # Update confidence scores based on context strength
        for rel in unique_relationships:
            rel.confidence = self._calculate_confidence(rel, text)

        # Sort by confidence
        unique_relationships.sort(key=lambda r: r.confidence, reverse=True)

        return unique_relationships

    def _calculate_confidence(self, relationship: NLPRelationship, text: str) -> float:
        """Calculate confidence score for a relationship based on context."""
        base_confidence = relationship.confidence

        # Boost confidence for strong relationship indicators
        strong_indicators = {
            'composition': ['contains', 'owns', 'manages', 'controls'],
            'inheritance': ['extends', 'inherits', 'is a type of'],
            'association': ['uses', 'references', 'connects'],
            'aggregation': ['collection of', 'group of', 'has multiple']
        }

        indicators = strong_indicators.get(relationship.relationship_type, [])
        context_lower = relationship.context.lower()

        for indicator in indicators:
            if indicator in context_lower:
                base_confidence = min(base_confidence + 0.1, 1.0)
                break

        # Reduce confidence for ambiguous relationships
        ambiguous_words = ['maybe', 'perhaps', 'possibly', 'could', 'might']
        for word in ambiguous_words:
            if word in context_lower:
                base_confidence = max(base_confidence - 0.2, 0.1)
                break

        return base_confidence