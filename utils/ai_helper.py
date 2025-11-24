from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def get_response(query: str) -> list[str]:
    """
    gets AI response using DeepSeek API
    
    args:
        query: user's prompt
        system_prompt: system message to set AI behavior
        
    returns:
        list of strings (split into chunks if > 2000 chars for Discord)
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": query},
            ],
            stream=False
        )

        full_response = response.choices[0].message.content
        
        # split response if it exceeds Discord's 2000 character limit
        if len(full_response) > 2000:
            split_response = [full_response[i:i+2000] for i in range(0, len(full_response), 2000)]
            return split_response
        else:
            return [full_response]
            
    except Exception as e:
        return [f"Error getting AI response: {str(e)}"]