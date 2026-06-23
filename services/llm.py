from transformers import pipeline

class ChatModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.pipe = pipeline("text-generation", model=model_name)
        print(f"[OK] LLM loaded: {model_name}")

    def generate(self, user_text: str, lang: str, emotion: str, history: list) -> str:
        hist = ""
        for turn in history[-4:]:
            hist += f"User: {turn['u']}\nAssistant: {turn['b']}\n"

        if lang == "ta":
            sys = (
                "நீ ஒரு ஆதரவான mental-health assistant (therapist அல்ல). "
                "மருத்துவ diagnosis/மருந்து ஆலோசனை வேண்டாம். "
                "பயனர் சொன்ன விஷயத்தை நேரடியாக பிரதிபலித்து பேசு. "
                "1) 1 வரியில் empathy 2) 1 practical step 3) 1 short question. "
                "Self-harm/crisis இல்லாமல் 'therapist' சொல்லாதே. "
                "பதில் 3-6 வரிகள் மட்டும்."
            )
            prompt = f"""{sys}

Conversation:
{hist}
User (emotion={emotion}): {user_text}

Assistant (Tamil):"""
        else:
            sys = (
                "You are a supportive mental-health assistant (not a therapist). "
                "No medical diagnosis or medication advice. "
                "Respond directly to the user's message (no generic filler). "
                "Format: 1) empathy in 1 line, 2) 1 practical step, 3) 1 short question. "
                "Do NOT mention therapist unless user mentions self-harm/crisis. "
                "Keep it 3-6 lines."
            )
            prompt = f"""{sys}

Conversation:
{hist}
User (emotion={emotion}): {user_text}

Assistant:"""

        out = self.pipe(
            prompt,
            max_new_tokens=160,
            do_sample=True,
            temperature=0.9,
            top_p=0.92
        )[0]["generated_text"].strip()
        return out
