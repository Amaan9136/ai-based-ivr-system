from flask import Blueprint, render_template, request, jsonify, session
import re
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_karnataka_schools
from helpers.voice_helpers import generate_tts_audio, translate_text_to_session_language, translate_text_to_english
from helpers.data_helpers import save_admission_request

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


@bp.route('/ask', methods=['POST'])
def chatbot_response():
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        old_summary = data.get('old_response_summary', '')
        conversation_state = data.get('conversation_state', {})

        print("[USER:]", prompt)

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

        # Translate user's prompt to English (for consistent intent detection / embeddings)
        try:
            translated_prompt_for_intent = translate_text_to_english(prompt, language)
            print("[USER LANG TO ENG]", translated_prompt_for_intent)
        except Exception as e:
            print(f"[Translation Error] {e}")
            translated_prompt_for_intent = prompt

        intent = match_intent(translated_prompt_for_intent)

        # === FIND SCHOOLS ===
        if intent == "find_schools":
            results = chroma_karnataka_schools(prompt)
            if results:
                def clean(value):
                    if isinstance(value, str) and '-' in value:
                        return value.split('-', 1)[-1].strip()
                    return value

                raw_data = "\n".join(
                    f"- {clean(r['school_name'])} in {clean(r['village'])}, {clean(r['block'])}, {clean(r['district'])}, located at {clean(r['location'])}, "
                    f"managed by {clean(r['state_mgmt'])}, category: {clean(r['school_category'])}, type: {clean(r['school_type'])}"
                    for r in results
                )

                print("[raw_data] ",raw_data)

                additional_instructions = (
                    "First apologize for making user to wait. "
                    "You are given raw school data. Your task is to extract structured information and present it in well-formed sentence format suitable for NLP processing. "
                    "The output must include the following details: school name, village, block, district, location, state management, school category, and school type. "
                    f"DATA: {raw_data} "
                    "Format each output sentence clearly and consistently. Use only lowercase letters in the entire response. Store the result in `new_response`."
                    "Also store the provided school DATA in old_response_summary too while summarizing as text"
                )

                chat_result = chat_with_history(
                    role="School Finder and Admission Assistant",
                    prompt=prompt,
                    additional_instructions=additional_instructions,
                    old_summary=old_summary
                )

                translated_response = translate_text_to_session_language(chat_result['new_response'], language)

                # Generate audio (always use lang_code for TTS)
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
