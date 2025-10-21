"""
BM25 Sparse Retrieval Implementation
Reference: Robertson et al., "Okapi at TREC-3", NIST Special Publication 500-225, 1995
Formula: BM25(d,q) = Σ IDF(qi) × (f(qi,d)×(k1+1))/(f(qi,d)+k1×(1-b+b×|d|/avgdl))
"""

from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from typing import List, Dict, Optional, Set
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BM25Result:
    """BM25 search result with metadata"""
    doc_id: str
    score: float
    rank: int
    text: str
    language: str

class MultilingualTokenizer:
    """
    Multilingual tokenizer supporting English, Arabic, Spanish
    """
    def __init__(self):
        self._use_nltk = True
        self.stopwords: Dict[str, Set[str]] = {}

        fallback_stopwords = {
            'en': {'the', 'a', 'an', 'and', 'of', 'to', 'in', 'is', 'for', 'on'},
            'es': {'el', 'la', 'los', 'las', 'de', 'y', 'en', 'que', 'es'},
            'ar': {'و', 'في', 'من', 'على', 'أن', 'هو', 'هي'},
        }

        try:
            # Ensure stopwords and punkt tokeniser are available. If downloads are
            # blocked (e.g. in CI without internet) we fall back to simple tokenisation.
            stopwords.words('english')
            stopwords.words('spanish')
            stopwords.words('arabic')
            nltk.data.find('tokenizers/punkt')

            self.stopwords = {
                'en': set(stopwords.words('english')),
                'es': set(stopwords.words('spanish')),
                'ar': set(stopwords.words('arabic')),
            }
        except Exception:
            logger.warning("NLTK resources unavailable, using fallback stopwords.")
            self._use_nltk = False
            self.stopwords = fallback_stopwords
    
    def tokenize(self, text: str, language: str = 'en') -> List[str]:
        """
        Tokenize text for given language
        
        Args:
            text: Input text to tokenize
            language: Language code ('en', 'ar', 'es')
        
        Returns:
            List of tokens (lowercased, no stopwords)
        """
        # Lowercase and basic cleaning
        text = text.lower()
        
        # Handle Arabic-specific preprocessing
        if language == 'ar':
            # Remove Arabic diacritics (tashkeel)
            text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
            # Normalize Arabic characters
            text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
            text = text.replace('ة', 'ه')
        
        tokens: List[str]
        if self._use_nltk:
            try:
                tokens = word_tokenize(text)
            except LookupError:
                logger.warning("word_tokenize failed; switching to regex tokeniser.")
                self._use_nltk = False
                tokens = re.findall(r"\w+", text, flags=re.UNICODE)
        else:
            tokens = re.findall(r"\w+", text, flags=re.UNICODE)
        
        # Remove stopwords and non-alphanumeric tokens
        tokens = [
            token for token in tokens 
            if token.isalnum() and token not in self.stopwords.get(language, set())
        ]
        
        return tokens

class BM25Retriever:
    """
    BM25 retrieval implementation with multilingual support
    
    Parameters:
        k1 (float): Term frequency saturation parameter (default: 1.5)
        b (float): Length normalization parameter (default: 0.75)
    
    Reference:
        Robertson, S. E., & Walker, S. (1994). Some simple effective 
        approximations to the 2-poisson model for probabilistic weighted 
        retrieval. In SIGIR'94.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.tokenizer = MultilingualTokenizer()
        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[Dict] = []
        self.tokenized_corpus: List[List[str]] = []
        self.doc_ids: List[str] = []
        
        logger.info(f"Initialized BM25Retriever with k1={k1}, b={b}")
    
    def index_documents(self, documents: List[Dict]) -> None:
        """
        Index documents for BM25 retrieval
        
        Args:
            documents: List of dicts with keys: id, text, language, metadata
                Example: [
                    {
                        "id": "doc1",
                        "text": "Document content...",
                        "language": "en",
                        "metadata": {"source": "file.pdf", "page": 1}
                    }
                ]
        """
        logger.info(f"Indexing {len(documents)} documents...")

        if not documents:
            self.documents = []
            self.tokenized_corpus = []
            self.doc_ids = []
            self.bm25 = None
            return
        
        self.documents = documents
        self.doc_ids = [doc['id'] for doc in documents]
        
        # Tokenize all documents
        self.tokenized_corpus = [
            self.tokenizer.tokenize(doc['text'], doc.get('language', 'en'))
            for doc in documents
        ]
        
        # Initialize BM25 with tokenized corpus
        self.bm25 = BM25Okapi(
            self.tokenized_corpus,
            k1=self.k1,
            b=self.b
        )
        
        logger.info(f"✅ Successfully indexed {len(documents)} documents")
        logger.info(f"   Average document length: {self.bm25.avgdl:.2f} tokens")

    # Backwards compatibility for older code/tests calling `.index(...)`
    def index(self, documents: List[Dict]) -> None:
        """Alias for index_documents."""
        self.index_documents(documents)
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        language: str = 'en',
        min_score: float = 0.0
    ) -> List[BM25Result]:
        """
        Search documents using BM25 scoring
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            language: Query language ('en', 'ar', 'es')
            min_score: Minimum BM25 score threshold
        
        Returns:
            List of BM25Result objects sorted by score (descending)
        """
        if self.bm25 is None or not self.documents:
            logger.info("Search requested before indexing; returning empty result.")
            return []
        
        # Tokenize query
        tokenized_query = self.tokenizer.tokenize(query, language)
        logger.info(f"Query tokens: {tokenized_query}")

        if not tokenized_query:
            logger.info("Empty tokenised query; returning empty result set.")
            return []
        
        # Get BM25 scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k document indices
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        # Build results
        results = []
        for rank, idx in enumerate(top_indices, start=1):
            score = scores[idx]
            if score > min_score:
                doc = self.documents[idx]
                doc_language = doc.get('language', 'en')
                if language and doc_language != language:
                    continue
                results.append(BM25Result(
                    doc_id=doc['id'],
                    score=float(score),
                    rank=rank,
                    text=doc['text'],
                    language=doc_language
                ))
        
        logger.info(f"Found {len(results)} results with score >= {min_score}")
        return results
    
    def get_document_score(self, query: str, doc_id: str, language: str = 'en') -> float:
        """Get BM25 score for a specific document"""
        tokenized_query = self.tokenizer.tokenize(query, language)
        
        # Find document index
        doc_idx = next(
            (i for i, doc in enumerate(self.documents) if doc['id'] == doc_id),
            None
        )
        
        if doc_idx is None:
            return 0.0
        
        scores = self.bm25.get_scores(tokenized_query)
        return float(scores[doc_idx])

    def clear_index(self) -> None:
        """Remove all indexed documents and reset the BM25 model."""
        self.documents = []
        self.tokenized_corpus = []
        self.bm25 = None
        logger.info("Cleared BM25 index")
