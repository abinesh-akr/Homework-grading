import nltk
from nltk import pos_tag, word_tokenize
from nltk.tokenize import sent_tokenize

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def parse_sentence(sentence):
    """Parses a sentence using NLTK and returns a grammar score."""
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)

    # Check if sentence is well-formed
    if len(tokens) > 0:
        score = 5  # Assuming it's grammatically correct
    else:
        score = compute_score(tagged)

    return score

def compute_score(tagged):
    """Computes a score based on part-of-speech tags."""
    num_of_words = len(tagged)
    num_of_nouns = sum(1 for word, tag in tagged if tag.startswith('NN'))
    num_of_verbs = sum(1 for word, tag in tagged if tag.startswith('VB'))

    # Simple scoring logic based on the number of nouns and verbs
    if num_of_words == 0:
        return 1
    link_ratio = (num_of_nouns + num_of_verbs) / num_of_words

    # Placeholder logic for scoring based on link ratio
    if link_ratio >= 0.5:
        score = 4
    elif 0.25 <= link_ratio < 0.5:
        score = 3
    else:
        score = 2

    return score

def check_grammar(sentence):
    """Checks basic grammar and punctuation errors."""
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    score = 5  # Default perfect score

    for word, tag in tagged:
        if tag == "CC" and word.lower() not in ["and", "but", "or"]:
            score -= 1  # Incorrect conjunction usage

        if tag == "Punctuation" and word == ",":
            score -= 1  # Incorrect comma placement

    return max(1, score)

def get_grammar_score(essay):
    """Evaluates an essay and returns an average grammar score."""
    sentences = sent_tokenize(essay)
    sent_scores = {}

    for sentence in sentences:
        sent_scores[sentence] = min(parse_sentence(sentence), check_grammar(sentence))

    avg_score = sum(sent_scores.values()) / max(1, len(sent_scores))
    return avg_score, sent_scores

# Example Usage
if __name__ == "__main__":
    essay = "This is a test sentence. This are incorrect grammar."
    
    cumscore, sentscore = get_grammar_score(essay)

    for key, value in sentscore.items():
        print(f"{key} :: {value}")

    print(f"Overall Score: {cumscore}")
