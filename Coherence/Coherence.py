import stanza
from sentence_transformers import SentenceTransformer
import numpy as np

# Load Stanza NLP pipeline

nlp = stanza.Pipeline(lang="en", processors="tokenize")

# Load pre-trained Sentence-BERT model
sentence_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

def check_coherence(essay, key):
    """Calculates coherence score using logic consistency and semantic similarity."""
    # Extract sentences using Stanza
    doc = nlp(essay)
    sentences = [" ".join([word.text for word in sentence.words]) for sentence in doc.sentences]

    # Logic consistency score based on logical connectors
    logic_consistency_score = calculate_logic_consistency(sentences)

    # Semantic similarity using Sentence-BERT
    
    semantic_similarity_score = calculate_semantic_similarity(key, sentences)

    # Normalize logic consistency score
    max_score = 5
    logic_consistency_score = min(logic_consistency_score, max_score) / max_score
    semantic_similarity_score = min(semantic_similarity_score, max_score) / max_score
    # Final coherence score
    coherence_score = ((logic_consistency_score + semantic_similarity_score) / 2) * 5

    return coherence_score

def calculate_logic_consistency(sentences):
    """Checks logical consistency by detecting logical connectors."""
    logic_consistency_score = 0

    for sentence in sentences:
        if has_logical_connectors(sentence):
            logic_consistency_score += 1
            print(f"Logical connection found: {sentence}")

    return logic_consistency_score

def has_logical_connectors(sentence):
    """Detects logical connectors in a sentence."""
    logical_connectors = [
        "but", "however", "although", "yet", "while", "even though",
        "on the other hand", "in contrast", "nevertheless",
        "nonetheless", "conversely", "still", "despite", "in spite of"
    ]
    
    return any(conn in sentence.lower() for conn in logical_connectors)

def calculate_semantic_similarity(key, sentences):
    """Calculates semantic similarity using Sentence-BERT."""
    if not sentences:
        return 0

    key_embedding = sentence_model.encode([key])
    sentence_embeddings = sentence_model.encode(sentences)

    cosine_similarities = np.dot(sentence_embeddings, key_embedding.T).flatten()
    avg_similarity = np.mean(cosine_similarities)

    print(f"Semantic Similarity Score: {avg_similarity}")

    return avg_similarity

def get_logical_sentences(essay):
    """Extracts sentences with logical connectors."""
    doc = nlp(essay)
    sentences = [" ".join([word.text for word in sentence.words]) for sentence in doc.sentences]

    logical_sentences = [{"sentence": s, "score": 1} for s in sentences if has_logical_connectors(s)]
    
    return logical_sentences

if __name__ == "__main__":
    # Example usage
    sourceFileName = "Sample_Essays/technology.txt"
    with open(sourceFileName, "r", encoding="utf-8") as sourceFile:
        essay = sourceFile.read()

    key = "Technology plays a significant role in modern life."  # Example key sentence

    coherence_score = check_coherence(essay, key)
    logical_sentences = get_logical_sentences(essay)

    print(f"Coherence Score: {coherence_score}")

    for logical_sentence in logical_sentences:
        print(f"Logical Sentence: {logical_sentence['sentence']}")
        print(f"Logical Sentence Score: {logical_sentence['score']}\n")
