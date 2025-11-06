import re
from typing import List

class TextPreprocessor:
    def __init__(self):
        self.technical_terms = set()
        self.software_patterns = [
            r'\b(class|interface|extends|implements|inherits)\b',
            r'\b(has a|have|contains|contain|manages|manage)\b',
            r'\b(user|users|account|accounts|product|products|order|orders)\b',
            r'\b(system|systems|service|services|api|apis|endpoint|endpoints)\b',
            r'\b(database|databases|table|tables|model|models)\b'
        ]

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize input text for NLP processing."""
        if not text:
            return ""

        # Step 1: Basic cleanup
        text = self._clean_text(text)

        # Step 2: Handle technical terms
        text = self._preserve_technical_terms(text)

        # Step 3: Normalize software patterns
        text = self._normalize_software_patterns(text)

        # Step 4: Extract and preserve technical terms for later use
        self._extract_technical_terms(text)

        return text.strip()

    def _clean_text(self, text: str) -> str:
        """Basic text cleaning operations."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common formatting issues
        text = re.sub(r'\s*([,.!?;:])\s*', r'\1 ', text)

        # Remove non-printable characters except common punctuation
        text = re.sub(r'[^\w\s,.!?;:\-\'"(){}[\]<>]', ' ', text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text

    def _preserve_technical_terms(self, text: str) -> str:
        """Preserve compound technical terms that might be split by NLP."""
        # Common software compound terms
        compound_terms = {
            'REST API': 'REST_API',
            'user interface': 'user_interface',
            'user account': 'user_account',
            'shopping cart': 'shopping_cart',
            'order details': 'order_details',
            'connection pooling': 'connection_pooling',
            'microservices': 'microservices',
            'database server': 'database_server'
        }

        for compound, normalized in compound_terms.items():
            text = text.replace(compound, normalized, flags=re.IGNORECASE)

        return text

    def _normalize_software_patterns(self, text: str) -> str:
        """Normalize common software description patterns."""
        # Normalize relationship indicators
        relationship_patterns = {
            r'\b(is comprised of|is made up of|consists of)\b': 'contains',
            r'\b(is part of|belongs to)\b': 'belongs_to',
            r'\b(talks to|communicates with|connects to)\b': 'connects_to',
            r'\b(is a type of|is a kind of)\b': 'is_a_type_of',
            r'\b(multiple|many|various)\s+(\w+)\b': r'many_\2',
            r'\b(optional|may have|can have)\s+(\w+)\b': r'optional_\2'
        }

        for pattern, replacement in relationship_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _extract_technical_terms(self, text: str) -> None:
        """Extract technical terms for better entity recognition."""
        # Extract capitalized terms that might be class names
        capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        self.technical_terms.update(capitalized_words)

        # Extract camelCase terms
        camelcase_words = re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', text)
        self.technical_terms.update(camelcase_words)

        # Extract words with underscores
        underscore_words = re.findall(r'\b[a-z]+_[a-z_]+\b', text)
        self.technical_terms.update(underscore_words)

        # Extract acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        self.technical_terms.update(acronyms)

    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split text into chunks for BERT processing (max 512 tokens)."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            if end >= len(text):
                chunks.append(text[start:])
                break

            # Try to break at sentence boundaries
            chunk = text[start:end]
            sentence_end = max(
                chunk.rfind('.'),
                chunk.rfind('!'),
                chunk.rfind('?')
            )

            if sentence_end > chunk_size * 0.7:  # If we found a good sentence break
                end = start + sentence_end + 1
                chunks.append(text[start:end])
            else:
                chunks.append(chunk)

            start = end - overlap if end < len(text) else end

        return chunks

    def get_technical_terms(self) -> List[str]:
        """Return list of identified technical terms."""
        return list(self.technical_terms)