import os
import json
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def remove_code_block_markers(content):
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        return '\n'.join(lines[1:-1])
    return content

def send_openai_request(prompt: str, model: str = 'gpt-4o-mini-2024-07-18') -> str:
    try:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = completion.choices[0].message.content
        print(f"Raw content from OpenAI API: {content}")  # Debug print
        if not content:
            return json.dumps({"error": "OpenAI returned an empty response."})
        
        # Remove code block markers if present
        content = remove_code_block_markers(content)
        
        # Attempt to parse the content as JSON
        try:
            parsed_content = json.loads(content)
            return json.dumps(parsed_content)
        except json.JSONDecodeError:
            # If parsing fails, wrap the content in a JSON object
            return json.dumps({"result": content})
    
    except Exception as e:
        return json.dumps({"error": f"OpenAI API error: {str(e)}"})
