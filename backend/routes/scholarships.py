from flask import Blueprint, render_template, request, jsonify, session
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_indian_scholarships
from helpers.voice_helpers import generate_tts_audio, translate_text_to_session_language, translate_text_to_english

bp = Blueprint('scholarships', __name__, url_prefix='/scholarships')

@bp.route('/')
def index():
    return render_template('components/scholarships.html')


@bp.route('/ask', methods=['POST'])
def chatbot_response():
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        old_summary = data.get('old_response_summary', '')
        conversation_state = data.get('conversation_state', {})

        print("[INFO] Received prompt:", prompt)

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

        translated_prompt = translate_text_to_english(prompt, language)
        print("[INFO] Translated Prompt:", translated_prompt)

        print("[INFO] Fetching scholarship data from Chroma RAG...")
        results = chroma_indian_scholarships(translated_prompt)

        if not results:
            msg = "I couldn’t find any relevant scholarships. Please provide more details like eligibility or scholarship amount."
            return jsonify({
                'status': 'success',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'old_response_summary': old_summary,
                'conversation_state': conversation_state
            })

        print(f"[INFO] {len(results)} scholarships fetched")

        def clean(value):
            if isinstance(value, str):
                return value.split("-", 1)[-1].strip() if "-" in value else value.strip()
            return value

        raw_data = "\n".join(
            f"Name: {clean(r.get('Name'))}; "
            f"Eligibility: {clean(r.get('Eligibility'))}; "
            f"Amount: {clean(r.get('Amount'))}; "
            f"Deadline: {clean(r.get('Deadline'))}; "
            f"Documents Required: {clean(r.get('Documents Required'))}"
            for r in results
        )

        print("[DEBUG] Raw Data:\n", raw_data)

        additional_instructions = (
            "You are an assistant for providing scholarship information based on available data. "
            "You have a dataset with details of scholarships, including Name, Eligibility, Amount, Deadline, and Documents Required."
            f"USE DATA:{raw_data} "
            "Given the following raw scholarship data, summarize the scholarships as clearly as possible, "
            "Please include the following fields for each scholarship: "
            "Name, Eligibility, Amount, Deadline, and Documents Required."    
        )

        print("[INFO] Sending prompt to chat_with_history...")

        chat_result = chat_with_history(
            role="Scholarship Finder and Admission Assistant",
            prompt=translated_prompt,
            additional_instructions=additional_instructions,
            old_summary=old_summary
        )

        translated_response = translate_text_to_session_language(chat_result['new_response'], language)
        audio_base64 = generate_tts_audio(translated_response, lang=lang_code)

        return jsonify({
            'status': 'success',
            'response': translated_response,
            'audio': audio_base64,
            'old_response_summary': chat_result['old_response_summary'],
            'conversation_state': conversation_state
        })

    except Exception as e:
        print(f"[ERROR] Internal server error: {e}")
        msg = "An internal error occurred while processing your request."
        return jsonify({
            'status': 'error',
            'response': msg,
            'audio': generate_tts_audio(msg, lang="en")
        }), 500
