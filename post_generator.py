import sys
import json
import os
from datetime import datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
from llm_helper import llm
from data.few_shot import FewShotPosts

# Initialize few-shot example manager
few_shot = FewShotPosts()

# Ensure history directory exists
HISTORY_DIR = Path("data/history")
HISTORY_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = HISTORY_DIR / "post_history.json"

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"


def get_prompt(length, language, tag, tone="Professional", hashtags=True, custom_instructions=""):
    length_str = get_length_str(length)

    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble or explanations - just the post content.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    4) Tone: {tone}
    5) Include hashtags: {"Yes" if hashtags else "No"}
    '''
    
    if language == "Hinglish":
        prompt += "Note: Hinglish means a mix of Hindi and English. The script should always be in English characters."
    
    if custom_instructions:
        prompt += f"\n6) Additional instructions: {custom_instructions}"

    examples = few_shot.get_filtered_posts(length, language, tag)

    if len(examples) > 0:
        prompt += "\n\nUse the writing style from these examples:"

    for i, post in enumerate(examples):
        post_text = post['text']
        prompt += f'\n\nExample {i+1}:\n{post_text}'

        if i == 1:  # Use max two samples
            break

    return prompt


def generate_post(length, language, tag, tone="Professional", hashtags=True, custom_instructions=""):
    """Generate a LinkedIn post with the given parameters"""
    prompt = get_prompt(length, language, tag, tone, hashtags, custom_instructions)
    
    # Optional: Pass any model parameters
    response = llm.invoke(prompt)
    return response.content


def save_post_history(post_data):
    """Save generated post to history"""
    # Add timestamp
    post_data['timestamp'] = datetime.now().isoformat()
    
    # Load existing history
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Add new post and save
    history.append(post_data)
    
    # Keep only last 50 posts
    if len(history) > 50:
        history = history[-50:]
        
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)


def get_post_history():
    """Get post history"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


if __name__ == "__main__":
    post = generate_post("Short", "English", "Job Search", "Professional", True)
    print(post)