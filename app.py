from flask import Flask, render_template, request
from openai import OpenAI
import os
import re

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🤖 AI FUNCTION
def ai_analyze(text):
    try:
        prompt = f"""
You are a top Instagram creator whose reels get millions of views.

Write hooks that feel raw, emotional, and scroll-stopping.
Do NOT sound like AI. Sound like a real person.

Analyze this reel idea: "{text}"

Give response STRICTLY in this format:

Score: X/10

Problems:
- Write 2-3 real, specific problems about the idea
- Keep them short and natural

Suggestions:
Give 7 HIGHLY viral hooks
Each hook must be short (under 10 words)
Use strong emotions: curiosity, fear, pain, urgency
Use "you" to directly target viewer
Make some hooks slightly controversial or bold
Add pattern interrupts like ❌ 😳 🔥

Hook Type:
Give ONLY ONE word:
Curiosity / Fear / Relatable / Authority

IMPORTANT:
- Do not repeat instructions
- Do not repeat instructions
- Hooks must feel human
- Avoid robotic tone
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


# 🧠 FLEXIBLE PARSER (IMPORTANT FIX)
def parse_ai_output(text):
    score = 0
    problems = []
    suggestions = []
    hook_type = ""

    # Score
    match = re.search(r"Score:\s*(\d+)", text)
    if match:
        score = int(match.group(1))

    # Problems
    problems_section = re.search(r"Problems:(.*?)Suggestions:", text, re.S)
    if problems_section:
        lines = problems_section.group(1).strip().split("\n")
        for line in lines:
            line = line.strip()
            if line:
                line = re.sub(r"^[-\d\.\)\s]+", "", line)  # remove -, 1., etc
                problems.append(line)

    # Suggestions (🔥 FIXED)
    suggestions_section = re.search(r"Suggestions:(.*?)Hook Type:", text, re.S)
    if suggestions_section:
        lines = suggestions_section.group(1).strip().split("\n")
        for line in lines:
            line = line.strip()
            if line:
                line = re.sub(r"^[-\d\.\)\s]+", "", line)  # remove numbering
                line = line.replace("(", "").replace(")", "")  # clean brackets
                suggestions.append(line)

    # Hook Type
    hook_match = re.search(r"Hook Type:\s*-?\s*(.*)", text)
    if hook_match:
        hook_type = hook_match.group(1).strip()

    return score, problems, suggestions, hook_type

# 🏠 HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')


# 🔍 ANALYZE ROUTE
@app.route('/analyze', methods=['POST'])
def analyze():
    user_input = request.form['hook']

    ai_result = ai_analyze(user_input)

    print("===== AI OUTPUT =====")
    print(ai_result)
    print("=====================")

    score, problems, suggestions, hook_type = parse_ai_output(ai_result)

    return render_template(
        'result.html',
        original=user_input,
        score=score,
        problems=problems,
        suggestions=suggestions,
        hook_type=hook_type
    )


# ▶️ RUN APP
if __name__ == '__main__':
    app.run(debug=True)