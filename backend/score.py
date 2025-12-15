import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


print("Loading local model (downloading first run only)...")
model = SentenceTransformer('all-MiniLM-L6-v2') 

def evaluate_transcripts(transcript_list, rubric_json_path):
    """
    Evaluate answers based on vector similarity (Semantic Search) 
    without using external APIs.
    """
    
    # Load Rubrik
    with open(rubric_json_path, 'r') as f:
        rubric_data = json.load(f)
    
    scores_list = []
    reasons_list = []
    
    print(f"\nStarting assessment for {len(transcript_list)} answers...")

    for index, transcript_text in enumerate(transcript_list):
        if index >= len(rubric_data): break
            
        current_rubric = rubric_data[index]
        rubric_criteria = current_rubric['rubric'] 
        
        rubric_texts = []
        rubric_scores_key = []
        
        for score_key, description in rubric_criteria.items():
            # Skip if description is empty/None
            if description:
                rubric_texts.append(description)
                rubric_scores_key.append(int(score_key))
        
        if not rubric_texts:
            scores_list.append(0)
            reasons_list.append("Tidak ada deskripsi rubrik.")
            continue

        # Tokenization
        student_embedding = model.encode([transcript_text]) 
        
        # Vector description section
        rubric_embeddings = model.encode(rubric_texts)
        
        # Calculate similarity with cosine similarity
        # The result is an array of similarities between student answers and [desc_4, desc_3, desc_2, desc_1]
        similarities = cosine_similarity(student_embedding, rubric_embeddings)[0]
        
        # Find the highest value (Which one is most similar to the description?)
        best_match_index = np.argmax(similarities)
        best_score = rubric_scores_key[best_match_index]
        similarity_percent = similarities[best_match_index] * 100
        
        # If the similarity is very low (e.g., < 15%), consider the answer irrelevant (Score 0 or 1)
        if similarity_percent < 15:
            final_score = 1
            final_reason = f"Answer {current_rubric['id']} was found to be irrelevant to any of the rubric criteria."
        else:
            final_score = best_score
            matched_desc = rubric_texts[best_match_index]
            final_reason = f"{matched_desc[:100]}."

        print(f"Answer {current_rubric['id']} has been evaluated")

        scores_list.append(final_score)
        reasons_list.append(final_reason)

    return scores_list, reasons_list

