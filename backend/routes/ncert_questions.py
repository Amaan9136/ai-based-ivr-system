from flask import Blueprint, render_template, request, jsonify, session
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_ncert_books
from helpers.voice_helpers import generate_tts_audio, translate_text_to_session_language, translate_text_to_english
from helpers.llm import generate_response
from helpers.email_helper import send_email
import re

bp = Blueprint('ncert_questions', __name__, url_prefix='/ncert-questions')

def contains_phrase(prompt, phrases):
    prompt_lower = prompt.lower()
    return any(phrase in prompt_lower for phrase in phrases)

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None


@bp.route('/')
def index():
    return render_template('components/ncert_questions.html')

@bp.route('/ask', methods=['POST'])
def ask_ncert_question():
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        old_summary = data.get('old_response_summary', '')
        conversation_state = data.get('conversation_state', {})

        print("\n🔹 USER:", prompt)

        input_language = data.get("language")
        if input_language:
            session['language'] = input_language.lower()

        language = session.get('language', 'english').lower()
        lang_code = {"english": "en", "hindi": "hi", "kannada": "kn"}.get(language, "en")

        if not prompt:
            msg = 'Please provide a question.'
            return jsonify({
                'status': 'error',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code)
            }), 400

        # Handle email-related intent first
        email_triggers = ["send email", "email this", "can i get email", "email me", "mail this", "please email"]
        user_email = extract_email(prompt)

        # 1. If user requests email but hasn't asked anything yet
        if contains_phrase(prompt, email_triggers):
            if not session.get("ncert_raw_data"):
                msg = "You didn’t ask anything about the topic yet."
                return jsonify({
                    'status': 'no_data',
                    'response': msg,
                    'audio': generate_tts_audio(msg, lang=lang_code),
                    'conversation_state': conversation_state
                })

            msg = "Sure! Please provide your email address."
            return jsonify({
                'status': 'awaiting_email',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'conversation_state': conversation_state
            })

        # 2. If prompt contains an email address (detected via regex)
        if user_email:
            if not session.get("ncert_raw_data"):
                msg = "You didn’t ask anything about the topic yet."
                return jsonify({
                    'status': 'error',
                    'response': msg,
                    'audio': generate_tts_audio(msg, lang=lang_code)
                }), 400

            session['email'] = user_email
            session['confirmed_email'] = False

            confirm_prompt = f"The user entered the email: {user_email}. Ask the user to confirm if this is correct by checking the spelling."
            confirm_msg = generate_response(confirm_prompt)  # You can still use chat_with_history if you want contextual style

            return jsonify({
                'status': 'awaiting_confirmation',
                'response': confirm_msg,
                'audio': generate_tts_audio(confirm_msg, lang=lang_code),
                'conversation_state': conversation_state
            })

        # 3. If user confirms email spelling
        confirmation_keywords = ["yes", "yeah", "yep", "yup", "correct", "go ahead", "okay", "sure", "confirm"]
        if contains_phrase(prompt, confirmation_keywords) and session.get("email") and not session.get("confirmed_email"):
            session['confirmed_email'] = True
            raw_data = session.get("ncert_raw_data", "")
            if raw_data:
                sent = send_email(session['email'], raw_data)
                msg = "✅ Email has been sent to your address!" if sent else "❌ Failed to send the email."
            else:
                msg = "There is no NCERT data to send."
            return jsonify({
                'status': 'email_sent',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'conversation_state': conversation_state
            })

        # 4. If unclear response during email confirmation step
        if session.get("email") and not session.get("confirmed_email"):
            msg = "I didn't get that. Could you please confirm if the email is correct?"
            return jsonify({
                'status': 'awaiting_confirmation',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'conversation_state': conversation_state
            })

        ### ----------- NCERT QUESTION LOGIC BELOW -----------

        # Translate prompt to English
        try:
            translated_prompt = translate_text_to_english(prompt, language)
            print("🔸 USER LANG TO ENGLISH:", translated_prompt)
        except Exception as e:
            print(f"[Translation Error] {e}")
            translated_prompt = prompt

        results = chroma_ncert_books(translated_prompt)

        if results:
            raw_data = "\n".join(
                f"TOPIC: {r['Topic']}\nEXPLANATION: {r['Explanation']}\nQUESTION: {r['Question']}\nANSWER: {r['Answer']}\n"
                f"SUBJECT: {r['subject']}, GRADE: {r['grade']}\n"
                for r in results
            )
            print("[raw_data] ", raw_data)
            session['ncert_raw_data'] = raw_data

            additional_instructions = (
                "You are an NCERT educational assistant. Based on the user query and the content provided, "
                f"NCERT DATA:\n{raw_data} "
                "generate a clear, helpful, and appropriate response using the provided content. "
                "Explain the entire topic in 200 - 300 words like notes for students. "
                "Store the full DATA in old_response_summary while summarizing as text."
            )

            chat_result = chat_with_history(
                role="NCERT Question Answering Assistant",
                prompt=prompt,
                additional_instructions=additional_instructions,
                old_summary=old_summary
            )

            translated_response = translate_text_to_session_language(chat_result['new_response'], language)
            follow_up = "Would you like me to email these notes to you?"

            return jsonify({
                'status': 'success',
                'response': translated_response + "\n\n" + follow_up,
                'audio': generate_tts_audio(translated_response + " " + follow_up, lang=lang_code),
                'old_response_summary': chat_result['old_response_summary'],
                'conversation_state': conversation_state
            })

        else:
            msg = "Sorry, I couldn’t find anything in the NCERT content related to your question. Try rephrasing or asking something else."
            print("⚠️ NO MATCH FOUND")
            return jsonify({
                'status': 'success',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'old_response_summary': old_summary,
                'conversation_state': conversation_state
            })

    except Exception as e:
        print(f"[❌ ERROR] {e}")
        msg = "An error occurred while processing your NCERT question."
        return jsonify({
            'status': 'error',
            'response': msg,
            'audio': generate_tts_audio(msg, lang="en")
        }), 500
