import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import List, Dict, Any
import logging
import re
from ..models.nlp_result import NLPEntity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BERTExtractor:
    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize BERT model for entity recognition.

        Args:
            model_name: Hugging Face model name for NER
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.ner_pipeline = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_model()

    def _load_model(self):
        """Load BERT model and tokenizer lazily."""
        try:
            logger.info(f"Loading BERT model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)

            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=0 if self.device.type == 'cuda' else -1
            )
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            self.ner_pipeline = None

    def extract_entities(self, text: str) -> List[NLPEntity]:
        """
        Extract entities (classes, attributes, methods) from text using BERT NER.

        Args:
            text: Input requirement text

        Returns:
            List of extracted entities with confidence scores
        """
        if not self.ner_pipeline:
            logger.warning("BERT pipeline not available, using rule-based extraction")
            return self._rule_based_extraction(text)

        entities = []

        try:
            # Use BERT NER pipeline
            ner_results = self.ner_pipeline(text)

            # Convert BERT entities to our format
            for entity in ner_results:
                nl_entity = self._convert_bert_entity(entity, text)
                if nl_entity:
                    entities.append(nl_entity)

            # Post-process to identify classes vs attributes
            entities = self._post_process_entities(entities, text)

        except Exception as e:
            logger.error(f"BERT extraction failed: {e}")
            return self._rule_based_extraction(text)

        return entities

    def _convert_bert_entity(self, bert_entity: Dict[str, Any], text: str) -> NLPEntity:
        """Convert BERT NER entity to our NLPEntity format."""
        entity_type = self._map_bert_label_to_uml(bert_entity['entity_group'])

        if entity_type:
            return NLPEntity(
                text=bert_entity['word'],
                label=entity_type,
                confidence=bert_entity['score'],
                start=bert_entity['start'],
                end=bert_entity['end']
            )
        return None

    def _map_bert_label_to_uml(self, bert_label: str) -> str:
        """Map BERT NER labels to UML-related labels."""
        label_mapping = {
            'PER': 'CLASS',      # Person/User
            'ORG': 'CLASS',      # Organization/System
            'LOC': 'CLASS',      # Location/Database
            'MISC': 'CLASS',     # Miscellaneous entities as classes
            'PRODUCT': 'CLASS',  # Products, services
            'EVENT': 'CLASS',    # Events, transactions
            'WORK_OF_ART': 'CLASS'  # Named systems, interfaces
        }

        return label_mapping.get(bert_label, 'CLASS')

    def _post_process_entities(self, entities: List[NLPEntity], text: str) -> List[NLPEntity]:
        """Post-process entities to identify attributes and methods."""
        processed_entities = []

        # Group entities by their text (case-insensitive)
        entity_groups = {}
        for entity in entities:
            key = entity.text.lower()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)

        # Consolidate similar entities
        for group in entity_groups.values():
            # Keep the one with highest confidence
            best_entity = max(group, key=lambda e: e.confidence)
            processed_entities.append(best_entity)

        # Identify attributes (typically appear with ownership indicators)
        processed_entities = self._identify_attributes(processed_entities, text)

        # Identify methods (typically verbs or action words)
        processed_entities = self._identify_methods(processed_entities, text)

        return processed_entities

    def _identify_attributes(self, entities: List[NLPEntity], text: str) -> List[NLPEntity]:
        """Identify which entities are attributes of classes."""
        class_entities = [e for e in entities if e.label == 'CLASS']
        attribute_patterns = [
            r'\b(\w+)\s+(of|for|in|from)\s+(' + '|'.join([c.text for c in class_entities]) + r')\b',
            r'\b(' + '|'.join([c.text for c in class_entities]) + r')\'?s?\s+(\w+)\b',
            r'\b(\w+)\s+(attribute|field|property)\b'
        ]

        new_entities = list(entities)

        for pattern in attribute_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    # Determine which group is the attribute and which is the class
                    if groups[0].lower() in [c.text.lower() for c in class_entities]:
                        attr_name = groups[1]
                        class_name = groups[0]
                    else:
                        attr_name = groups[0]
                        class_name = groups[1] if len(groups) > 1 else None

                    # Check if attribute already exists
                    if not any(e.text.lower() == attr_name.lower() for e in new_entities):
                        attr_entity = NLPEntity(
                            text=attr_name,
                            label='ATTRIBUTE',
                            confidence=0.8,
                            start=match.start(),
                            end=match.end(),
                            belongs_to=class_name
                        )
                        new_entities.append(attr_entity)

        return new_entities

    def _identify_methods(self, entities: List[NLPEntity], text: str) -> List[NLPEntity]:
        """Identify methods (typically verbs or action words)."""
        method_patterns = [
            r'\b(\w+)\s+(method|function|operation)\b',
            r'\b(\w+)\s+(action|process|execute|perform)\b',
            r'\b(can|should|will|must)\s+(\w+)\b',
            r'\b(login|logout|register|create|update|delete|save|get|set|calculate|validate|check|send|receive)\b'
        ]

        new_entities = list(entities)

        for pattern in method_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                method_name = groups[-1]  # Take the last group as method name

                if not any(e.text.lower() == method_name.lower() for e in new_entities):
                    method_entity = NLPEntity(
                        text=method_name,
                        label='METHOD',
                        confidence=0.7,
                        start=match.start(),
                        end=match.end()
                    )
                    new_entities.append(method_entity)

        return new_entities

    def _rule_based_extraction(self, text: str) -> List[NLPEntity]:
        """Fallback rule-based entity extraction when BERT is not available."""
        entities = []

        # Extract potential class names (capitalized words, technical terms)
        class_patterns = [
            r'\b[A-Z][a-zA-Z]+\b',  # Capitalized words
            r'\b\w+[A-Z]\w*\b',     # camelCase
            r'\b\w+_\w+\b',         # snake_case
            r'\b[A-Z]{2,}\b'        # Acronyms
        ]

        for pattern in class_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                word = match.group()
                if len(word) > 2:  # Filter out short words
                    entity = NLPEntity(
                        text=word,
                        label='CLASS',
                        confidence=0.6,
                        start=match.start(),
                        end=match.end()
                    )
                    entities.append(entity)

        # Extract attributes (typically follow possession patterns)
        attr_patterns = [
            r'\b(\w+)\s+(of|for|in)\s+(\w+)\b',
            r'\b(\w+)\'s\s+(\w+)\b'
        ]

        for pattern in attr_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    attr_name = groups[0] if groups[0] != 'user' else groups[1]
                    entity = NLPEntity(
                        text=attr_name,
                        label='ATTRIBUTE',
                        confidence=0.5,
                        start=match.start(),
                        end=match.end()
                    )
                    entities.append(entity)

        return entities