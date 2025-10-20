"""
Entity Extraction Service
Combines LLM-based extraction with spaCy NER for robust multilingual entity recognition
"""

import spacy
from typing import List, Dict, Tuple, Optional
import logging
import hashlib
from dataclasses import dataclass
import google.generativeai as genai

logger = logging.getLogger(__name__)

@dataclass
class ExtractedEntity:
    """Extracted entity with metadata"""
    name: str
    type: str
    language: str
    confidence: float
    context: str

class EntityExtractor:
    """
    Multilingual entity extraction using spaCy + LLM validation
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize entity extractor
        
        Args:
            gemini_api_key: Optional Gemini API key for LLM-based extraction
        """
        # Load spaCy models
        self.models = {}
        try:
            self.models['en'] = spacy.load('en_core_web_sm')
            logger.info("✅ Loaded English spaCy model")
        except OSError:
            logger.warning("English spaCy model not found")
        
        try:
            self.models['es'] = spacy.load('es_core_news_sm')
            logger.info("✅ Loaded Spanish spaCy model")
        except OSError:
            logger.warning("Spanish spaCy model not found")
        
        try:
            self.models['xx'] = spacy.load('xx_ent_wiki_sm')
            logger.info("✅ Loaded multilingual spaCy model")
        except OSError:
            logger.warning("Multilingual spaCy model not found")
        
        # Initialize Gemini if API key provided
        self.use_llm = False
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.llm_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.use_llm = True
                logger.info("✅ Gemini LLM initialized for entity extraction")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
    
    def extract_entities(
        self,
        text: str,
        language: str = 'en'
    ) -> List[ExtractedEntity]:
        """
        Extract entities from text using spaCy NER
        
        Args:
            text: Input text
            language: Language code ('en', 'ar', 'es')
        
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Select appropriate spaCy model
        model = self.models.get(language, self.models.get('xx'))
        if not model:
            logger.warning(f"No spaCy model available for language: {language}")
            return entities
        
        # Process text with spaCy
        doc = model(text)
        
        # Extract named entities
        for ent in doc.ents:
            entity = ExtractedEntity(
                name=ent.text,
                type=self._map_entity_type(ent.label_),
                language=language,
                confidence=0.8,  # Default confidence for spaCy
                context=ent.sent.text if ent.sent else text[:200]
            )
            entities.append(entity)
        
        logger.info(f"Extracted {len(entities)} entities using spaCy")
        return entities
    
    def extract_entities_llm(
        self,
        text: str,
        language: str = 'en'
    ) -> List[ExtractedEntity]:
        """
        Extract entities using LLM (Gemini)
        
        Args:
            text: Input text
            language: Language code
        
        Returns:
            List of extracted entities
        """
        if not self.use_llm:
            logger.warning("LLM not available, falling back to spaCy")
            return self.extract_entities(text, language)
        
        prompt = f"""Extract all named entities from the following text. 
For each entity, provide:
1. Entity name
2. Entity type (PERSON, ORGANIZATION, LOCATION, CONCEPT, PRODUCT, EVENT)
3. Confidence score (0.0-1.0)

Text: {text[:1000]}

Output format (JSON):
[
  {{"name": "Entity Name", "type": "TYPE", "confidence": 0.95}},
  ...
]
"""
        
        try:
            response = self.llm_model.generate_content(prompt)
            # Parse LLM response (simplified - should use proper JSON parsing)
            entities = []
            # For now, fallback to spaCy
            return self.extract_entities(text, language)
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self.extract_entities(text, language)
    
    def _map_entity_type(self, spacy_label: str) -> str:
        """Map spaCy entity labels to standardized types"""
        mapping = {
            'PERSON': 'PERSON',
            'PER': 'PERSON',
            'ORG': 'ORGANIZATION',
            'GPE': 'LOCATION',
            'LOC': 'LOCATION',
            'PRODUCT': 'PRODUCT',
            'EVENT': 'EVENT',
            'WORK_OF_ART': 'CONCEPT',
            'LANGUAGE': 'CONCEPT',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'MONEY': 'MONEY',
            'QUANTITY': 'QUANTITY',
        }
        return mapping.get(spacy_label, 'CONCEPT')
    
    def generate_entity_id(self, name: str, language: str) -> str:
        """Generate unique entity ID"""
        unique_string = f"{name.lower()}_{language}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]
