"""Vector memory for storing and retrieving interview Q&A pairs."""
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceEmbeddings


class VectorMemory:
    """Vector store for managing Q&A pairs during interviews."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector memory.
        
        Args:
            model_name: HuggingFace embedding model name
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.qa_pairs = []  # List of {"question": q, "answer": a}
        self.stopwords = {
            'the', 'and', 'for', 'you', 'your', 'can', 'with', 'that', 'this',
            'from', 'have', 'had', 'been', 'they', 'their', 'what', 'when', 'how',
            'why', 'are', 'was', 'will', 'would', 'could', 'should', 'about',
            'also', 'there', 'which', 'more', 'than', 'such', 'those', 'these',
            'were', 'while', 'where', 'into', 'onto', 'over', 'under'
        }

    def add_qa(self, question: str, answer: str) -> None:
        """Add Q&A pair to memory."""
        self.qa_pairs.append({"question": question, "answer": answer})

    def is_duplicate_topic(self, new_question: str) -> bool:
        """Check if new question is duplicate of existing topics."""
        new_keywords = self._extract_keywords(new_question)

        for past in self.qa_pairs:
            past_keywords = self._extract_keywords(past["question"])
            overlap = len(new_keywords.intersection(past_keywords))
            if overlap >= 3:
                return True  # Considered duplicate
        return False

    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text, filtering stopwords."""
        words = text.lower().split()
        return set(
            word.strip(".,!?()[]\"'") for word in words
            if len(word) > 3 and word not in self.stopwords
        )
