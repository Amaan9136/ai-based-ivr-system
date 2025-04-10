from flask import Blueprint, render_template, request, jsonify, session
import re
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_karnataka_schools
from helpers.voice_helpers import generate_tts_audio
from routes.language_routes import get_language

bp = Blueprint('nearby_schools', __name__, url_prefix='/nearby-schools')

REQUIRED_FIELDS = ["student_name", "phone", "address"]
INTENT_KEYWORDS = {
    "find_schools": ["find", "school", "near", "nearby", "area", "location", "in my locality"],
    "admission": ["admission", "apply", "submit", "enroll"]
}

def match_intent(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return intent
    return "default"

def extract_fields_from_prompt(prompt: str, missing_fields: list) -> dict:
    result = {}
    for field in missing_fields:
        if field == "phone":
            match = re.search(r'\b\d{10}\b', prompt)
            if match:
                result["phone"] = match.group()
        elif field == "student_name":
            match = re.search(r"\b(?:my name is|student name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", prompt, re.I)
            if match:
                result["student_name"] = match.group(1)
        elif field == "address":
            match = re.search(r"(?:address is|near|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", prompt, re.I)
            if match:
                result["address"] = match.group(1)
    return result

@bp.route('/')
def index():
    return render_template('components/nearby_schools.html')

@bp.route('/nearby_school_finder', methods=['POST'])
def chatbot_response():
    data = request.json
    prompt = data.get('prompt', '').strip()
    old_summary = data.get('old_response_summary', '')
    conversation_state = data.get('conversation_state', {})

    if not prompt:
        return jsonify({'status': 'error', 'response': 'Please provide a question.'}), 400

    try:
        intent = match_intent(prompt)

        if intent == "find_schools":
            results = chroma_karnataka_schools(prompt)
            if results:
                school_data = "\n".join(
                    f"- {r['school_name']} in {r['village']}, {r['block']}, {r['district']}, located at {r['location']}, managed by {r['state_mgmt']}, category: {r['school_category']}, type: {r['school_type']}"
                    for r in results
                )

                print(school_data)

                additional_instructions = (
                    "You are given raw school data. Your task is to extract structured information and present it in well-formed sentence format suitable for NLP processing. "
                    "The output must include the following details: school name, village, block, district, location, state management, school category, and school type. "
                    f"Raw data: {school_data} "
                    "Format each output sentence clearly and consistently. Use only lowercase letters in the entire response. Store the result in `new_response`."
                )


                chat_result = chat_with_history(
                    role="School Assistant",
                    prompt=prompt,
                    additional_instructions=additional_instructions,
                    old_summary=old_summary
                )

                language = get_language().get_json()["language"]
                print(language)
                lang_code = "hi" if language == "hindi" else "kn" if language == "kannada" else "en"
                audio_base64 = generate_tts_audio(chat_result['new_response'], lang=lang_code)

                return jsonify({
                    'status': 'success',
                    'response': chat_result['new_response'],
                    'audio': audio_base64,
                    'old_response_summary': chat_result['old_response_summary'],
                    'conversation_state': conversation_state
                })
            else:
                return jsonify({
                    'status': 'success',
                    'response': "I couldn’t find any relevant schools. Please provide more details like village, block, or pincode.",
                    'old_response_summary': old_summary,
                    'conversation_state': conversation_state
                })

        if intent == "admission":
            conversation_state["admission_mode"] = True
            missing_fields = [f for f in REQUIRED_FIELDS if f not in conversation_state]
            extracted = extract_fields_from_prompt(prompt, missing_fields)

            for k, v in extracted.items():
                conversation_state[k] = v

            still_missing = [f for f in REQUIRED_FIELDS if f not in conversation_state]
            if still_missing:
                return jsonify({
                    'status': 'success',
                    'response': f"To proceed, please provide: {', '.join(still_missing)}.",
                    'old_response_summary': old_summary,
                    'conversation_state': conversation_state
                })

            msg = (
                f"Thanks! Admission request submitted for {conversation_state['student_name']}.\n"
                f"We'll contact you at {conversation_state['phone']} about schools near {conversation_state['address']}."
            )

            language = get_language().get_json()["language"]
            lang_code = "hi" if language == "hindi" else "kn" if language == "kannada" else "en"
            audio_base64 = generate_tts_audio(msg, lang=lang_code)

            return jsonify({
                'status': 'success',
                'response': msg,
                'audio': audio_base64,
                'old_response_summary': old_summary,
                'conversation_state': {}  # Reset
            })

        chat_result = chat_with_history(
            role="School Assistant",
            prompt=prompt,
            additional_instructions="",
            old_summary=old_summary
        )

        language = get_language().get_json()["language"]
        lang_code = "hi" if language == "hindi" else "kn" if language == "kannada" else "en"
        audio_base64 = generate_tts_audio(chat_result['new_response'], lang=lang_code)

        return jsonify({
            'status': 'success',
            'response': chat_result['new_response'],
            'audio': audio_base64,
            'old_response_summary': chat_result['old_response_summary'],
            'conversation_state': conversation_state
        })

    except Exception as e:
        print(f"[Error] {e}")
        return jsonify({
            'status': 'error',
            'response': 'An internal error occurred while processing your request.'
        }), 500
