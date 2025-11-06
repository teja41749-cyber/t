from typing import List, Dict, Any

class NLPEntity:
    def __init__(self, text: str, label: str, confidence: float, start: int, end: int, belongs_to: str = None):
        self.text = text
        self.label = label  # CLASS, ATTRIBUTE, METHOD
        self.confidence = confidence
        self.start = start
        self.end = end
        self.belongs_to = belongs_to  # For attributes/methods, which class they belong to

class NLPRelationship:
    def __init__(self, source: str, target: str, relationship_type: str, confidence: float, context: str = ""):
        self.source = source
        self.target = target
        self.relationship_type = relationship_type  # composition, association, inheritance, aggregation
        self.confidence = confidence
        self.context = context  # The sentence or phrase where this was found

class NLPResult:
    def __init__(self):
        self.entities: List[NLPEntity] = []
        self.relationships: List[NLPRelationship] = []
        self.processed_text: str = ""
        self.metadata: Dict[str, Any] = {}

    def add_entity(self, entity: NLPEntity):
        self.entities.append(entity)

    def add_relationship(self, relationship: NLPRelationship):
        self.relationships.append(relationship)

    def get_entities_by_label(self, label: str) -> List[NLPEntity]:
        return [entity for entity in self.entities if entity.label == label]

    def get_classes(self) -> List[NLPEntity]:
        return self.get_entities_by_label("CLASS")

    def get_attributes(self) -> List[NLPEntity]:
        return self.get_entities_by_label("ATTRIBUTE")

    def get_methods(self) -> List[NLPEntity]:
        return self.get_entities_by_label("METHOD")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'entities': [
                {
                    'text': entity.text,
                    'label': entity.label,
                    'confidence': entity.confidence,
                    'start': entity.start,
                    'end': entity.end,
                    'belongs_to': entity.belongs_to
                } for entity in self.entities
            ],
            'relationships': [
                {
                    'source': rel.source,
                    'target': rel.target,
                    'relationship_type': rel.relationship_type,
                    'confidence': rel.confidence,
                    'context': rel.context
                } for rel in self.relationships
            ],
            'processed_text': self.processed_text,
            'metadata': self.metadata
        }