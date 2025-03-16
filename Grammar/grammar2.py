import stanza

# Download English model if not already available


# Load the Stanza pipeline
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

def parse_sentence(sentence):
    """Parses a sentence using Stanza and returns a grammar score."""
    doc = nlp(sentence)

    # Check if sentence is well-formed
    if len(doc.sentences) > 0:
        score = 5  # Assuming it's grammatically correct
    else:
        score = compute_score(doc)

    return score

def compute_score(doc):
    """Computes a score based on dependency relations and grammar heuristics."""
    num_of_words = sum(len(sentence.words) for sentence in doc.sentences)
    num_of_dependencies = sum(len(sentence.dependencies) for sentence in doc.sentences)

    link_ratio = num_of_dependencies / max(1, num_of_words)

    # Placeholder logic for scoring based on link ratio
    if link_ratio >= 1.0:
        score = 4
    elif 0.5 <= link_ratio < 1.0:
        score = 3
    elif 0.25 <= link_ratio < 0.5:
        score = 2
    else:
        score = 1

    return score

def check_grammar(sentence):
    """Checks basic grammar and punctuation errors."""
    doc = nlp(sentence)
    score = 5  # Default perfect score

    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos == "CCONJ" and word.text.lower() not in ["and", "but", "or"]:
                score -= 1  # Incorrect conjunction usage

            if word.upos == "PUNCT" and word.text == ",":
                score -= 1  # Incorrect comma placement

    return max(1, score)

def getGrammarScore(essay):
    """Evaluates an essay and returns an average grammar score."""
    doc = nlp(essay)
    sent_scores = {}

    for sentence in doc.sentences:
        sentence_text = " ".join([word.text for word in sentence.words])
        sent_scores[sentence_text] = min(parse_sentence(sentence_text), check_grammar(sentence_text))

    avg_score = sum(sent_scores.values()) / max(1, len(sent_scores))
    return avg_score, sent_scores

# Example Usage
if __name__ == "__main__":
    essay = "This is a test sentence. This are incorrect grammar."
    
    cumscore, sentscore = getGrammarScore(essay)

    for key, value in sentscore.items():
        print(f"{key} :: {value}")

    print(f"Overall Score: {cumscore}")
