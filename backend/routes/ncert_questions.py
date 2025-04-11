from flask import Blueprint, render_template, request, jsonify, session
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_ncert_books
from helpers.voice_helpers import generate_tts_audio, translate_text_to_session_language, translate_text_to_english

bp = Blueprint('ncert_questions', __name__, url_prefix='/ncert-questions')

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

        try:
            translated_prompt = translate_text_to_english(prompt, language)
            print("🔸 USER LANG TO ENGLISH:", translated_prompt)
        except Exception as e:
            print(f"[Translation Error] {e}")
            translated_prompt = prompt

        # Search NCERT dataset
        results = chroma_ncert_books(translated_prompt)

        if results:
            raw_data = "\n".join(
                f"TOPIC: {r['Topic']}\nEXPLANATION: {r['Explanation']}\nQUESTION: {r['Question']}\nANSWER: {r['Answer']}\n"
                f"SUBJECT: {r['subject']}, GRADE: {r['grade']}, DIFFICULTY: {r['Difficulty']}\n"
                for r in results
            )

            print("[raw_data] ",raw_data)
            session['ncert_raw_data'] = raw_data  

            additional_instructions = (
                "First apologize for making user to wait. "
                "You are an NCERT educational assistant. Based on the user query and the content provided, "
                f"NCERT DATA:\n{raw_data}"
                "generate a clear, helpful, and appropriate response using the provided content. "
                "Ensure answers are factual, aligned with the NCERT syllabus, explaining entire topic as a notes in 200 - 300 words."
                "Also store the provided complete DATA in old_response_summary too while summarizing as text"
            )

            chat_result = chat_with_history(
                role="NCERT Question Answering Assistant",
                prompt=prompt,
                additional_instructions=additional_instructions,
                old_summary=old_summary
            )

            translated_response = translate_text_to_session_language(chat_result['new_response'], language)

            # Generate audio (always use lang_code for TTS)
            audio_base64 = generate_tts_audio(translated_response, lang=lang_code)

            print("✅ FINAL RESPONSE:", translated_response)

            return jsonify({
                'status': 'success',
                'response': translated_response,
                'audio': audio_base64,
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
