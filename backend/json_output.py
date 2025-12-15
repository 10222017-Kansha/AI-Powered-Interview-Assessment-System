import json
from datetime import datetime

def get_overall_summary(average_score):
    if average_score >= 3.5:
        description = "Candidate demonstrates comprehensive and deep technical understanding across most topics."
    elif average_score >= 2.5:
        description = "Candidate shows solid capability and good understanding, though some answers lacked specific details."
    elif average_score >= 1.5:
        description = "Candidate has basic familiarity with the concepts but responses were often general or vague."
    else:
        description = "Candidate demonstrated insufficient technical knowledge; many answers were minimal or incorrect."
        
    return f"Average Score: {average_score}. {description}"

def generate_final_assessment_report(
    input_payload,
    video_paths_dict, 
    transcriptions_list, 
    scores_list, 
    reasons_list
):
    try:
        # with open(input_payload, 'r') as f:
        #     payload = json.load(f)
        past_review_data = input_payload['data']['pastReviews'][0]
        
        assessor_profile = past_review_data['assessorProfile']
        decision = past_review_data['decision']
        reviewed_at = past_review_data['reviewedAt']
        
        # Take the project value (default 100 if none)
        project_score = past_review_data['scoresOverview'].get('project', 100)
        
    except (KeyError, IndexError):
        # Fallback if JSON structure is different/empty (Safety net)
        assessor_profile = {"id": 0, "name": "Unknown", "photoUrl": ""}
        decision = "Need Human"
        reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_score = 100
    
    # Scores overview 
    total_score_sum = sum(scores_list)
    num_questions = len(scores_list)
    
    # Calculate the average score (Scale 0-4) for "Overall Notes"
    if num_questions > 0:
        avg_score_raw = total_score_sum / num_questions
        average_score_val = round(avg_score_raw, 1)
    else:
        average_score_val = 0.0

    # Calculate Interview Score (Percentage 0-100)
    # Formula: [(total score)/(4 * number of questions)] * 100
    max_possible_score = 4 * num_questions
    if max_possible_score > 0:
        raw_interview_score = (total_score_sum / max_possible_score) * 100
    else:
        raw_interview_score = 0
        
    # Calculate Total Score
    # Formula: 0.7 * project + 0.3 * interview
    raw_total_score = (0.7 * project_score) + (0.3 * raw_interview_score)
    interview_score_final = round(raw_interview_score, 1)
    total_score_final = round(raw_total_score, 1)

    # Compiling answers
    detailed_scores_data = []
    sorted_ids = sorted(video_paths_dict.keys())
    
    for i, video_id in enumerate(sorted_ids):
        list_index = i 
        
        entry = {
            "id": video_id,
            "score": scores_list[list_index],
            "reason": reasons_list[list_index],
            "transcriptions": transcriptions_list[list_index],
        }
        detailed_scores_data.append(entry)

    # Generate "Overall Notes"
    overall_notes_text = get_overall_summary(average_score_val)
    
    final_json_structure = {
        "assessorProfile": {
            "id": assessor_profile['id'],
            "name": assessor_profile['name'],
            "photoUrl": assessor_profile['photoUrl']
        },
        "decision": decision,
        "reviewedAt": reviewed_at,
        "scoresOverview": {
            "project": project_score,
            "interview": interview_score_final,
            "total": total_score_final
        },
        "reviewChecklistResult": {
            "project": [],
            "interviews": {
                "minScore": min(scores_list),
                "maxScore": max(scores_list),
                "scores": detailed_scores_data
            }
        },
        "Overall notes": overall_notes_text 
    }
    
    return final_json_structure