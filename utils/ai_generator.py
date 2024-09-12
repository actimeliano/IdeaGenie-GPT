from openai_chat_completion.chat_request import send_openai_request
import json

def generate_content(initial_title, initial_idea, feedback, model="gpt-4o-mini-2024-07-18"):
    feedback_history = format_feedback(feedback)
    prompt = f"""
    Generate 5 new titles and 5 new ideas based on the following input:
    Initial Title: {initial_title}
    Initial Idea: {initial_idea}
    
    Previous feedback:
    {feedback_history}

    Use the feedback to refine and improve the generated content. Focus on aspects that received positive feedback and avoid those with negative feedback.

    Format the output as a JSON string with the following structure:
    {{
        "titles": ["title1", "title2", "title3", "title4", "title5"],
        "ideas": ["idea1", "idea2", "idea3", "idea4", "idea5"]
    }}
    """
    
    response = send_openai_request(prompt, model=model)
    response_data = json.loads(response)
    
    if "error" in response_data:
        raise ValueError(f"Error in OpenAI request: {response_data['error']}")
    
    if "result" in response_data:
        # The API returned a non-JSON response, so we'll need to parse it
        # You may need to implement custom parsing logic here
        return {"titles": [response_data["result"]], "ideas": [response_data["result"]]}
    
    return response_data

def classify_content(content, model="gpt-4o-mini-2024-07-18"):
    prompt = f"""
    Classify each title and idea into one of three categories: "normal", "edgy", or "ultra new".
    
    Titles: {json.dumps(content['titles'])}
    Ideas: {json.dumps(content['ideas'])}

    Format the output as a JSON string with the following structure:
    {{
        "titles": [
            {{"content": "title1", "category": "category1"}},
            {{"content": "title2", "category": "category2"}},
            ...
        ],
        "ideas": [
            {{"content": "idea1", "category": "category1"}},
            {{"content": "idea2", "category": "category2"}},
            ...
        ]
    }}
    """

    response = send_openai_request(prompt, model=model)
    return json.loads(response)

def format_feedback(feedback):
    formatted_feedback = ""
    for item in feedback:
        formatted_feedback += f"- Type: {item['type']}, Content: {item['content']}, Feedback: {item['feedback']}\n"
    return formatted_feedback
