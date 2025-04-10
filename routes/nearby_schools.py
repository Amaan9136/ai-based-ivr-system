from flask import Blueprint, render_template, request, jsonify, session
import re
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_karnataka_schools
from helpers.voice_helpers import generate_tts_audio, translate_text_to_session_language
from helpers.data_helpers import save_admission_request
from deep_translator import GoogleTranslator

bp = Blueprint('nearby_schools', __name__, url_prefix='/nearby-schools')

REQUIRED_FIELDS = ["student_name", "phone", "address"]

INTENT_KEYWORDS = {
    "find_schools": [
        "find", "school", "near", "nearby", "area", "location", "locality", "around me", 
        "search for schools", "locate school", "schools in", "close to me", "nearest school", 
        "lookup schools", "suggest schools", "schools near", "schools nearby", "good schools", 
        "schools available", "list of schools", "where is the school", "school finder"
    ],
    "admission": [
        "admission", "apply", "submit", "enroll", "enrollment", "admissions open", 
        "register", "registration", "how to join", "application process", "start admission", 
        "seeking admission", "fill form", "fill application", "join school", "how to apply", 
        "school entry", "when can I apply", "how to register", "apply for school"
    ]
}


def match_intent(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return intent
    return "default"


def extract_fields_from_prompt(prompt: str, missing_fields: list) -> dict:
    result = {}
    if "phone" in missing_fields:
        match = re.search(r'\b\d{10}\b', prompt)
        if match:
            result["phone"] = match.group()
    if "student_name" in missing_fields:
        match = re.search(r"\b(?:my name is|student name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", prompt, re.I)
        if match:
            result["student_name"] = match.group(1)
    if "address" in missing_fields:
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
        # Translate user's prompt to English (for consistent intent detection / embeddings)
        try:
            translated_prompt_for_intent = GoogleTranslator(source=language, target='english').translate(prompt)
        except Exception as e:
            print(f"[Translation Error] {e}")
            translated_prompt_for_intent = prompt

        intent = match_intent(translated_prompt_for_intent)

        # === FIND SCHOOLS ===
        if intent == "find_schools":
            results = chroma_karnataka_schools(prompt)
            if results:
                raw_data = "\n".join(
                    f"- {r['school_name']} in {r['village']}, {r['block']}, {r['district']}, located at {r['location']}, "
                    f"managed by {r['state_mgmt']}, category: {r['school_category']}, type: {r['school_type']}"
                    for r in results
                )

                additional_instructions = (
                    "First apologize for making user to wait. "
                    "You are given raw school data. Your task is to extract structured information and present it in well-formed sentence format suitable for NLP processing. "
                    "The output must include the following details: school name, village, block, district, location, state management, school category, and school type. "
                    f"Raw data: {raw_data} "
                    "Format each output sentence clearly and consistently. Use only lowercase letters in the entire response. Store the result in `new_response`."
                )

                chat_result = chat_with_history(
                    role="School Finder and Admission Assistant",
                    prompt=prompt,
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

            else:
                msg = "I couldn’t find any relevant schools. Please provide more details like village, block, or pincode."
                return jsonify({
                    'status': 'success',
                    'response': msg,
                    'audio': generate_tts_audio(msg, lang=lang_code),
                    'old_response_summary': old_summary,
                    'conversation_state': conversation_state
                })

        # === ADMISSION ===
        if intent == "admission":
            conversation_state["admission_mode"] = True
            missing_fields = [f for f in REQUIRED_FIELDS if f not in conversation_state]
            extracted = extract_fields_from_prompt(prompt, missing_fields)
            conversation_state.update(extracted)

            still_missing = [f for f in REQUIRED_FIELDS if f not in conversation_state]
            if still_missing:
                msg = f"To proceed, please provide: {', '.join(still_missing)}."
                return jsonify({
                    'status': 'success',
                    'response': msg,
                    'audio': generate_tts_audio(msg, lang=lang_code),
                    'old_response_summary': old_summary,
                    'conversation_state': conversation_state
                })

            save_admission_request({
                "student_name": conversation_state['student_name'],
                "phone": conversation_state['phone'],
                "address": conversation_state['address']
            })

            msg = (
                f"Thanks! Admission request submitted for {conversation_state['student_name']}.\n"
                f"We'll contact you at {conversation_state['phone']} about schools near {conversation_state['address']}."
            )

            return jsonify({
                'status': 'success',
                'response': msg,
                'audio': generate_tts_audio(msg, lang=lang_code),
                'old_response_summary': old_summary,
                'conversation_state': {}  # Reset
            })

        # === DEFAULT FALLBACK CHAT ===
        chat_result = chat_with_history(
            role="School Finder and Admission Assistant",
            prompt=prompt,
            additional_instructions="",
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
        print(f"[Error] {e}")
        msg = "An internal error occurred while processing your request."
        return jsonify({
            'status': 'error',
            'response': msg,
            'audio': generate_tts_audio(msg, lang=lang_code)
        }), 500
