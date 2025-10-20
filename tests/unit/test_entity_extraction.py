"""
Unit Tests for Entity Extraction
Tests entity extraction with spaCy models
"""

import pytest
from backend.services.entity_extraction import EntityExtractor, ExtractedEntity


@pytest.mark.unit
class TestEntityExtractor:
    """Test entity extraction functionality"""
    
    def test_initialization_without_api_key(self):
        """Test initialization without Gemini API key"""
        extractor = EntityExtractor()
        
        assert extractor.models is not None
        assert extractor.use_llm is False
    
    def test_initialization_with_api_key(self):
        """Test initialization with Gemini API key"""
        extractor = EntityExtractor(gemini_api_key="test-key")
        
        assert extractor.models is not None
        # LLM might not initialize with fake key, but should not crash
    
    def test_extract_entities_english(self):
        """Test entity extraction from English text"""
        extractor = EntityExtractor()
        text = "Apple Inc. was founded by Steve Jobs in California."
        
        entities = extractor.extract_entities(text, language='en')
        
        assert isinstance(entities, list)
        assert all(isinstance(e, ExtractedEntity) for e in entities)
        
        # Should extract at least some entities
        if entities:
            assert any(e.type in ['PERSON', 'ORGANIZATION', 'LOCATION'] for e in entities)
    
    def test_extract_entities_spanish(self):
        """Test entity extraction from Spanish text"""
        extractor = EntityExtractor()
        text = "Pablo Picasso nació en Málaga, España."
        
        entities = extractor.extract_entities(text, language='es')
        
        assert isinstance(entities, list)
        # Spanish model might extract entities
    
    def test_extract_entities_arabic(self):
        """Test entity extraction from Arabic text"""
        extractor = EntityExtractor()
        text = "محمد علي كان ملاكمًا مشهورًا من الولايات المتحدة."
        
        entities = extractor.extract_entities(text, language='ar')
        
        assert isinstance(entities, list)
        # Multilingual model should handle Arabic
    
    def test_extract_entities_empty_text(self):
        """Test extraction from empty text"""
        extractor = EntityExtractor()
        
        entities = extractor.extract_entities("", language='en')
        
        assert entities == []
    
    def test_extract_entities_no_entities(self):
        """Test extraction from text with no entities"""
        extractor = EntityExtractor()
        text = "This is a simple sentence with no names or places."
        
        entities = extractor.extract_entities(text, language='en')
        
        # Might return empty or few entities
        assert isinstance(entities, list)
    
    def test_entity_structure(self):
        """Test ExtractedEntity structure"""
        extractor = EntityExtractor()
        text = "Microsoft was founded by Bill Gates."
        
        entities = extractor.extract_entities(text, language='en')
        
        if entities:
            entity = entities[0]
            assert hasattr(entity, 'name')
            assert hasattr(entity, 'type')
            assert hasattr(entity, 'language')
            assert hasattr(entity, 'confidence')
            assert hasattr(entity, 'context')
            assert entity.language == 'en'
            assert 0 <= entity.confidence <= 1
    
    def test_entity_type_mapping(self):
        """Test entity type mapping"""
        extractor = EntityExtractor()
        
        # Test various entity types
        mapped = extractor._map_entity_type('PERSON')
        assert mapped == 'PERSON'
        
        mapped = extractor._map_entity_type('ORG')
        assert mapped == 'ORGANIZATION'
        
        mapped = extractor._map_entity_type('GPE')
        assert mapped == 'LOCATION'
        
        mapped = extractor._map_entity_type('UNKNOWN_TYPE')
        assert mapped == 'CONCEPT'
    
    def test_generate_entity_id(self):
        """Test entity ID generation"""
        extractor = EntityExtractor()
        
        id1 = extractor.generate_entity_id("Apple Inc", "en")
        id2 = extractor.generate_entity_id("Apple Inc", "en")
        id3 = extractor.generate_entity_id("Apple Inc", "es")
        
        # Same name and language should produce same ID
        assert id1 == id2
        
        # Different language should produce different ID
        assert id1 != id3
        
        # ID should be consistent length (16 chars from MD5)
        assert len(id1) == 16
    
    def test_entity_confidence_scores(self):
        """Test that confidence scores are within valid range"""
        extractor = EntityExtractor()
        text = "Amazon is a large company based in Seattle."
        
        entities = extractor.extract_entities(text, language='en')
        
        for entity in entities:
            assert 0 <= entity.confidence <= 1
    
    def test_unsupported_language_fallback(self):
        """Test fallback to multilingual model for unsupported language"""
        extractor = EntityExtractor()
        text = "This is test text."
        
        # Use unsupported language code
        entities = extractor.extract_entities(text, language='unsupported')
        
        # Should use multilingual model as fallback
        assert isinstance(entities, list)
    
    def test_long_text_handling(self):
        """Test handling of long text"""
        extractor = EntityExtractor()
        # Create long text
        text = "Steve Jobs founded Apple Inc. " * 100
        
        entities = extractor.extract_entities(text, language='en')
        
        # Should handle without crashing
        assert isinstance(entities, list)
    
    def test_special_characters_in_entities(self):
        """Test extraction with special characters"""
        extractor = EntityExtractor()
        text = "The company AT&T and CEO John O'Brien work together."
        
        entities = extractor.extract_entities(text, language='en')
        
        # Should extract entities with special chars
        assert isinstance(entities, list)
    
    def test_context_extraction(self):
        """Test that context is properly extracted"""
        extractor = EntityExtractor()
        text = "Steve Jobs founded Apple Inc in 1976. It became very successful."
        
        entities = extractor.extract_entities(text, language='en')
        
        for entity in entities:
            assert entity.context is not None
            assert len(entity.context) > 0


@pytest.mark.unit
class TestEntityExtractionEdgeCases:
    """Test edge cases in entity extraction"""
    
    def test_multiple_entities_same_name(self):
        """Test handling of multiple occurrences of same entity"""
        extractor = EntityExtractor()
        text = "Apple released new products. Apple is innovative. Apple leads the market."
        
        entities = extractor.extract_entities(text, language='en')
        
        # Should extract entities (might have duplicates)
        assert isinstance(entities, list)
    
    def test_mixed_language_text(self):
        """Test extraction from mixed language text"""
        extractor = EntityExtractor()
        text = "Apple Inc (Estados Unidos) released products in España."
        
        entities = extractor.extract_entities(text, language='en')
        
        # Should handle mixed language reasonably
        assert isinstance(entities, list)
    
    def test_numbers_and_dates(self):
        """Test extraction of dates and numbers"""
        extractor = EntityExtractor()
        text = "The meeting is on January 15, 2024 at 3:00 PM with $1000 budget."
        
        entities = extractor.extract_entities(text, language='en')
        
        # spaCy might extract DATE, TIME, MONEY entities
        if entities:
            types = [e.type for e in entities]
            # Verify valid entity types
            assert all(t in ['DATE', 'TIME', 'MONEY', 'PERSON', 'ORGANIZATION', 
                            'LOCATION', 'CONCEPT', 'QUANTITY', 'PRODUCT', 'EVENT'] for t in types)
    
    def test_abbreviations_and_acronyms(self):
        """Test extraction of abbreviations and acronyms"""
        extractor = EntityExtractor()
        text = "The CEO of IBM, John Smith, attended the AI conference organized by MIT."
        
        entities = extractor.extract_entities(text, language='en')
        
        # Should extract both full names and acronyms
        assert isinstance(entities, list)
