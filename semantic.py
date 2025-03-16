from transformers import pipeline

# Load GPT model


def compute_gpt_similarity(key_answer, student_answer):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    print("key : " +key_answer )
    print("text : "+ student_answer)
    # Check if the student answer is too short or just contains a few keywords
    if len(student_answer.split()) < 3:  # You can adjust this threshold (e.g., 3 words)
        return 0.0  # Return 0% if it's too short or contains only a few keywords

    # If the student answer contains mostly keywords (e.g., very short meaningful content)
    keywords_only = len([word for word in student_answer.split() if word in key_answer]) < 2  # Detect if there are only a few meaningful words
    if keywords_only:
        return 20.0  # Assign a low accuracy (e.g., 20%) for answers that are only keywords

    result = classifier(student_answer, candidate_labels=[key_answer, "Contradiction"])

    # Take confidence score for the correct label (usually the first one)
    similarity_score = result["scores"][0] * 100

    # If the "Contradiction" score is higher than the key answer's score, reduce similarity
    if result["labels"][0] == "Contradiction" and result["scores"][0] > 0.7:
        similarity_score = 0.0  # Strong contradiction, return 0% similarity

    return str(round(similarity_score, 2))

