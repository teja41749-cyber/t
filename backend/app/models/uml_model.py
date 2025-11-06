from typing import List, Optional
from enum import Enum
from dataclasses import dataclass

class RelationshipType(Enum):
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"

@dataclass
class Attribute:
    name: str
    type: str = "String"
    visibility: str = "+"  # + public, - private, # protected
    is_static: bool = False

@dataclass
class Method:
    name: str
    parameters: List[str] = None
    return_type: str = "void"
    visibility: str = "+"
    is_static: bool = False

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

@dataclass
class Point:
    x: float
    y: float

@dataclass
class UMLClass:
    name: str
    attributes: List[Attribute] = None
    methods: List[Method] = None
    position: Point = None
    confidence: float = 1.0

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = []
        if self.methods is None:
            self.methods = []
        if self.position is None:
            self.position = Point(0, 0)

@dataclass
class UMLRelationship:
    source: str  # Class name
    target: str  # Class name
    type: RelationshipType
    multiplicity_source: str = "1"
    multiplicity_target: str = "1"
    label: str = ""
    confidence: float = 1.0

class UMLModel:
    def __init__(self):
        self.classes: List[UMLClass] = []
        self.relationships: List[UMLRelationship] = []

    def add_class(self, uml_class: UMLClass):
        # Check if class already exists
        existing = self.find_class(uml_class.name)
        if existing:
            # Merge attributes and methods
            existing.attributes.extend([attr for attr in uml_class.attributes if attr not in existing.attributes])
            existing.methods.extend([method for method in uml_class.methods if method not in existing.methods])
        else:
            self.classes.append(uml_class)

    def add_relationship(self, relationship: UMLRelationship):
        # Check if relationship already exists
        existing = self.find_relationship(relationship.source, relationship.target)
        if existing:
            existing.type = relationship.type
            existing.confidence = relationship.confidence
        else:
            self.relationships.append(relationship)

    def find_class(self, name: str) -> Optional[UMLClass]:
        for cls in self.classes:
            if cls.name.lower() == name.lower():
                return cls
        return None

    def find_relationship(self, source: str, target: str) -> Optional[UMLRelationship]:
        for rel in self.relationships:
            if (rel.source.lower() == source.lower() and
                rel.target.lower() == target.lower()):
                return rel
        return None

    def remove_class(self, name: str) -> bool:
        cls = self.find_class(name)
        if cls:
            self.classes.remove(cls)
            # Remove related relationships
            self.relationships = [rel for rel in self.relationships
                                 if rel.source != name and rel.target != name]
            return True
        return False

    def remove_relationship(self, source: str, target: str) -> bool:
        rel = self.find_relationship(source, target)
        if rel:
            self.relationships.remove(rel)
            return True
        return False

    def to_dict(self) -> dict:
        return {
            'classes': [
                {
                    'name': cls.name,
                    'attributes': [
                        {
                            'name': attr.name,
                            'type': attr.type,
                            'visibility': attr.visibility,
                            'is_static': attr.is_static
                        } for attr in cls.attributes
                    ],
                    'methods': [
                        {
                            'name': method.name,
                            'parameters': method.parameters,
                            'return_type': method.return_type,
                            'visibility': method.visibility,
                            'is_static': method.is_static
                        } for method in cls.methods
                    ],
                    'position': {'x': cls.position.x, 'y': cls.position.y},
                    'confidence': cls.confidence
                } for cls in self.classes
            ],
            'relationships': [
                {
                    'source': rel.source,
                    'target': rel.target,
                    'type': rel.type.value,
                    'multiplicity_source': rel.multiplicity_source,
                    'multiplicity_target': rel.multiplicity_target,
                    'label': rel.label,
                    'confidence': rel.confidence
                } for rel in self.relationships
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UMLModel':
        model = cls()

        # Add classes
        for cls_data in data.get('classes', []):
            uml_class = UMLClass(
                name=cls_data['name'],
                attributes=[
                    Attribute(
                        name=attr['name'],
                        type=attr.get('type', 'String'),
                        visibility=attr.get('visibility', '+'),
                        is_static=attr.get('is_static', False)
                    ) for attr in cls_data.get('attributes', [])
                ],
                methods=[
                    Method(
                        name=method['name'],
                        parameters=method.get('parameters', []),
                        return_type=method.get('return_type', 'void'),
                        visibility=method.get('visibility', '+'),
                        is_static=method.get('is_static', False)
                    ) for method in cls_data.get('methods', [])
                ],
                position=Point(
                    x=cls_data.get('position', {}).get('x', 0),
                    y=cls_data.get('position', {}).get('y', 0)
                ),
                confidence=cls_data.get('confidence', 1.0)
            )
            model.add_class(uml_class)

        # Add relationships
        for rel_data in data.get('relationships', []):
            relationship = UMLRelationship(
                source=rel_data['source'],
                target=rel_data['target'],
                type=RelationshipType(rel_data['type']),
                multiplicity_source=rel_data.get('multiplicity_source', '1'),
                multiplicity_target=rel_data.get('multiplicity_target', '1'),
                label=rel_data.get('label', ''),
                confidence=rel_data.get('confidence', 1.0)
            )
            model.add_relationship(relationship)

        return model