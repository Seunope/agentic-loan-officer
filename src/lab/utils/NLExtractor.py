import re
import spacy
from word2number import w2n
from typing import Dict, Any, Set, Optional, Tuple
import subprocess

class ApplicationExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            subprocess.call(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        self.patterns = {
            "age": [
                r"\b(?:I am|I'm|my age is|aged?)\s*(\d{1,2})\b",
                r"\b(\d{1,2})\s*(?:years old|year old|years|year)\b"
            ],
            "gender": [
                r"\b(?:I am|I'm|my gender is|gender:?)\s*(male|female|other)\b",
                r"\b(male|female|other)\b"
            ],
            "marital_status": [
                r"\b(?:I am|I'm|my status is|marital status:?)\s*(single|married|divorced|widowed)\b",
                r"\b(single|married|divorced|widowed)\b"
            ],
            "location": [
                r"\b(?:I live in|I am from|I'm from|I reside in|located in|city:?)\s*([A-Za-z\s]+(?:City)?)\b",
                r"\bin\s+([A-Za-z\s]+(?:City)?)\b"
            ],
            "amount": [
                r"\$\s*([\d,]+(?:\.\d+)?)",
                r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:dollars|USD|\$)",
                r"(?:loan|borrow|amount)(?:\s+of)?\s*\$?\s*([\d,]+(?:\.\d+)?)",
                r"(?:loan|borrow|amount)(?:\s+of)?\s*([\d,]+(?:\.\d+)?)\s*(?:dollars|USD|\$)"
            ],
            "tenure": [
                r"(\d+)\s*(?:day|days)",
                r"(\d+)\s*(?:month|months)",
                r"(\d+)\s*(?:year|years)",
                r"(?:term|tenure|period)(?:\s+of)?\s*(\d+)\s*(?:day|days)",
                r"(?:term|tenure|period)(?:\s+of)?\s*(\d+)\s*(?:month|months)",
                r"(?:term|tenure|period)(?:\s+of)?\s*(\d+)\s*(?:year|years)"
            ]
        }

        self.entity_map = {
            "AGE": "age",
            "CARDINAL": ["age", "amount", "tenure"],
            "MONEY": "amount",
            "GPE": "location",
            "PERSON": None,
            "DATE": None,
            "ORDINAL": None
        }

        self.field_keywords = {
            "age": ["age", "old", "year", "years"],
            "gender": ["gender", "male", "female", "other", "man", "woman", "nonbinary"],
            "marital_status": ["marital", "single", "married", "divorced", "widowed", "bachelor", "spouse"],
            "location": ["location", "city", "live", "residing", "address", "from", "located", "state"],
            "amount": ["amount", "loan", "borrow", "dollar", "money", "fund", "price", "cost"],
            "tenure": ["tenure", "tenor","month", "year", "term", "period", "duration", "time", "repayment"]
        }

        self.validators = {
            "age": lambda x: isinstance(x, (int, float)) and 18 < x < 100,
            "gender": lambda x: x.lower() in ["male", "female", "other"],
            "marital_status": lambda x: x.lower() in ["single", "married", "divorced", "widowed"],
            "location": lambda x: x.lower() in ["abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue", 
    "borno", "cross river", "delta", "ebonyi", "edo", "ekiti", "enugu", 
    "gombe", "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi", "kogi", 
                            "kwara", "lagos", "nasarawa", "niger", "ogun", "ondo", "osun", "oyo", 
                            "plateau", "rivers", "sokoto", "taraba", "yobe", "zamfara", "fct"],
            # "location": lambda x: isinstance(x, str) and 2 <= len(x) <= 50,
            "amount": lambda x: isinstance(x, (int, float)) and 0 < x <= 1000000,
            "tenure": lambda x: isinstance(x, (int, float)) and 0 < x <= 120
        }

        self.normalizers = {
            "age": lambda x: int(x),
            "gender": lambda x: x.lower(),
            "marital_status": lambda x: x.lower(),
            "location": lambda x: x.strip().title(),
            "amount": lambda x: float(str(x).replace(",", "")),
            "tenure": lambda x: int(x)
        }

    def _clean_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_with_patterns(self, field: str, text: str) -> Optional[str]:
        for pattern in self.patterns[field]:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        return None

    def _extract_with_nlp(self, field: str, doc) -> Optional[str]:
        if field == "gender":
            for token in doc:
                if token.text.lower() in ["male", "female", "other"]:
                    return token.text.lower()

        if field == "marital_status":
            for token in doc:
                if token.text.lower() in ["single", "married", "divorced", "widowed"]:
                    return token.text.lower()

        for ent in doc.ents:
            mapped_field = self.entity_map.get(ent.label_)

            if mapped_field == field:
                return ent.text

            if isinstance(mapped_field, list) and field in mapped_field:
                context = doc[max(0, ent.start-3):min(len(doc), ent.end+3)].text.lower()
                if any(kw in context for kw in self.field_keywords[field]):
                    return ent.text

        if field == "location":
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    return ent.text

        return None

    def _extract_with_context(self, field: str, doc) -> Optional[str]:
        field_keywords = self.field_keywords[field]

        for i, token in enumerate(doc):
            if token.is_stop or token.is_punct:
                continue

            context_start = max(0, i - 5)
            context_end = min(len(doc), i + 5)
            context = doc[context_start:context_end]

            if any(kw in token.text.lower() for kw in field_keywords):
                for nearby in context:
                    if nearby.like_num or nearby.is_digit:
                        if field in ["age", "amount", "tenure"]:
                            return nearby.text
                    elif field in ["gender", "marital_status", "location"]:
                        if field == "gender" and nearby.text.lower() in ["male", "female", "other"]:
                            return nearby.text
                        elif field == "marital_status" and nearby.text.lower() in ["single", "married", "divorced", "widowed"]:
                            return nearby.text
                        elif field == "location" and nearby.text.lower() in ["abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue", 
    "borno", "cross river", "delta", "ebonyi", "edo", "ekiti", "enugu", 
    "gombe", "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi", "kogi", 
                            "kwara", "lagos", "nasarawa", "niger", "ogun", "ondo", "osun", "oyo", 
                            "plateau", "rivers", "sokoto", "taraba", "yobe", "zamfara", "fct"]:
                            return nearby.text
                        

            if field == "location" and i > 0 and doc[i-1].text.lower() == "in" and token.pos_ == "PROPN":
                return token.text

        return None
    
    def extract_all_fields(self, text: str, fields_to_extract: Set[str], current_data: Dict[str, Any] = None) -> Dict[str, Tuple[Any, float]]:
        """
        Extract all specified fields from the text.
        
        Args:
            text: The input text to extract from
            fields_to_extract: Set of field names to extract
            current_data: Dictionary of already extracted data (to provide context)
        
        Returns:
            Dictionary mapping field names to tuples of (extracted_value, confidence_score)
        """
        if current_data is None:
            current_data = {}
            
        # Clean the text
        text = self._clean_text(text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        results = {}
        
        # Extract each requested field using multiple methods
        for field in fields_to_extract:
            if field not in self.patterns:
                continue
                
            # Try multiple extraction methods
            value = None
            confidence = 0.0
            
            # Method 1: Regular expression patterns
            pattern_value = self._extract_with_patterns(field, text)
            if pattern_value:
                value = pattern_value
                confidence = 0.8  # High confidence for regex matches
            
            # Method 2: NLP entity recognition
            if not value:
                nlp_value = self._extract_with_nlp(field, doc)
                if nlp_value:
                    value = nlp_value
                    confidence = 0.7  # Medium-high confidence for NLP entities
            
            # Method 3: Context-based extraction
            if not value:
                context_value = self._extract_with_context(field, doc)
                if context_value:
                    value = context_value
                    confidence = 0.6  # Medium confidence for contextual extraction
            
            # If a value was extracted, validate and normalize it
            if value:
                try:
                    # Handle special cases for amount (remove $ and commas)
                    if field == "amount" and isinstance(value, str):
                        value = value.replace("$", "").replace(",", "")
                    
                    # Try converting word numbers to digits if needed
                    if field in ["age", "amount", "tenure"] and isinstance(value, str):
                        try:
                            # First check if it's already a number
                            float(value)
                        except ValueError:
                            # If not, try word to number conversion
                            try:
                                value = str(w2n.word_to_num(value))
                            except:
                                pass
                    
                    # Normalize the value
                    normalized_value = self.normalizers[field](value)
                    
                    # Apply validation
                    if self.validators[field](normalized_value):
                        results[field] = (normalized_value, confidence)
                except (ValueError, TypeError):
                    # If normalization or validation fails, don't include this field
                    pass
        
        return results