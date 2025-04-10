<<<<<<< HEAD
from flask import Blueprint, render_template, request, jsonify
import re
from helpers.chatters import chat_with_history
from helpers.chroma_helpers import chroma_karnataka_schools

bp = Blueprint('nearby_schools', __name__, url_prefix='/nearby-schools')

REQUIRED_FIELDS_SCHOOL = ["district", "block_or_village", "location"]
REQUIRED_FIELDS_ADMISSION = ["student_name", "phone", "address"]

INTENT_KEYWORDS = {
    "find_schools": ["find", "school", "near", "nearby", "area", "location", "in my locality", "schools around", "school for me", "find me", "find my school"],
    "admission": ["admission", "apply", "submit", "enroll"]
}


=======
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

>>>>>>> master
def match_intent(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return intent
    return "default"

<<<<<<< HEAD

def extract_fields(prompt: str, required_fields: list, field_patterns: dict) -> dict:
    result = {}
    for field in required_fields:
        if field in field_patterns:
            for pattern in field_patterns[field]:
                match = re.search(pattern, prompt, re.I)
                if match:
                    result[field] = match.group(1).strip()
                    break
    return result


=======
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

>>>>>>> master
@bp.route('/')
def index():
    return render_template('components/nearby_schools.html')

<<<<<<< HEAD

@bp.route('/api/nearby_school_finder', methods=['POST'])
=======
@bp.route('/nearby_school_finder', methods=['POST'])
>>>>>>> master
def chatbot_response():
    data = request.json
    prompt = data.get('prompt', '').strip()
    old_summary = data.get('old_response_summary', '')
    conversation_state = data.get('conversation_state', {})

    if not prompt:
        return jsonify({'status': 'error', 'response': 'Please provide a question.'}), 400

    try:
        intent = match_intent(prompt)

<<<<<<< HEAD
        # === School Search Intent ===
        if intent == "find_schools":
            conversation_state["school_search_mode"] = True
            missing_fields = [f for f in REQUIRED_FIELDS_SCHOOL if f not in conversation_state]
            field_patterns = {
                "district": [r"(?:district is|in district|from district)\s+([A-Za-z\s]+)"],
                "block_or_village": [r"(?:block is|village is|it's|in|at)\s+([A-Za-z\s]+)"],
                "location": [r"(?:location is|location name is)\s+([A-Za-z\s]+)"]
            }

            extracted = extract_fields(prompt, missing_fields, field_patterns)
            conversation_state.update(extracted)

            # Even with partial data, run the query
            available_fields = [f for f in REQUIRED_FIELDS_SCHOOL if f in conversation_state and conversation_state[f]]
            search_terms = [conversation_state[f] for f in available_fields]
            search_query = ", ".join(search_terms).strip()
            
            print(search_query)

            if not available_fields:
                instruction = (
                    "User is trying to find schools but hasn't provided enough location details. "
                    "Ask for district, block or village, and location."
                )
                chat_result = chat_with_history(
                    role="School Assistant",
                    prompt=prompt,
                    old_summary=old_summary,
                    additional_instructions=instruction
                )
                return jsonify({
                    'status': 'success',
                    'response': chat_result['new_response'],
                    'old_response_summary': chat_result['old_response_summary'],
                    'conversation_state': conversation_state
                })

            results = chroma_karnataka_schools(search_query)

            if results and isinstance(results, list) and any("school_name" in r for r in results):
                school_data = "\n".join(
                    f"- {r['school_name']} in {r.get('village', 'Unknown')}, {r.get('block', 'Unknown')}, {r.get('district', 'Unknown')} - {r.get('udise_code', 'N/A')}"
                    for r in results
                )
                instructions = (
                    f"User asked about schools in {search_query}. Based on the following school data, generate a friendly, helpful response mentioning a few schools include them as lower case sentence if its uppercase:\n{school_data}"
                )
                chat_result = chat_with_history(
                    role="School Researcher and Assistant",
                    prompt=prompt,
                    old_summary=old_summary,
                    additional_instructions=instructions
                )
                return jsonify({
                    'status': 'success',
                    'response': chat_result['new_response'],
                    'old_response_summary': chat_result['old_response_summary'],
                    'conversation_state': {}
                })
            else:
                still_missing = [f for f in REQUIRED_FIELDS_SCHOOL if f not in conversation_state or not conversation_state[f]]
                if still_missing:
                    next_missing = still_missing[0]
                    instruction = f"Couldn't find school data with current info. Ask the user to provide their {next_missing}."
                else:
                    instruction = f"No school data found for: {search_query}. Kindly apologize and suggest trying with more specific details."
=======
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

>>>>>>> master

                chat_result = chat_with_history(
                    role="School Assistant",
                    prompt=prompt,
<<<<<<< HEAD
                    old_summary=old_summary,
                    additional_instructions=instruction
                )
                return jsonify({
                    'status': 'success',
                    'response': chat_result['new_response'],
                    'old_response_summary': chat_result['old_response_summary'],
                    'conversation_state': conversation_state
                })

        # === Admission Intent ===
        elif intent == "admission":
            conversation_state["admission_mode"] = True
            missing_fields = [f for f in REQUIRED_FIELDS_ADMISSION if f not in conversation_state]
            field_patterns = {
                "student_name": [r"(?:my name is|student name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"],
                "phone": [r"\b(\d{10})\b"],
                "address": [r"(?:address is|near|in)\s+([A-Za-z\s]+)"]
            }

            extracted = extract_fields(prompt, missing_fields, field_patterns)
            conversation_state.update(extracted)

            still_missing = [f for f in REQUIRED_FIELDS_ADMISSION if f not in conversation_state or not conversation_state[f]]
            if still_missing:
                next_missing = still_missing[0]
                instruction = f"User wants to submit an admission request. Kindly ask them to provide their {next_missing}."
                chat_result = chat_with_history(
                    role="Admission Assistant",
                    prompt=prompt,
                    old_summary=old_summary,
                    additional_instructions=instruction
                )
                return jsonify({
                    'status': 'success',
                    'response': chat_result['new_response'],
                    'old_response_summary': chat_result['old_response_summary'],
                    'conversation_state': conversation_state
                })

            # All admission details present
            instruction = (
                f"User wants to apply for admission with the following details:\n"
                f"Student Name: {conversation_state['student_name']}\n"
                f"Phone: {conversation_state['phone']}\n"
                f"Address: {conversation_state['address']}\n"
                f"Confirm and acknowledge their admission submission in a friendly tone."
            )
            chat_result = chat_with_history(
                role="Admission Assistant",
                prompt=prompt,
                old_summary=old_summary,
                additional_instructions=instruction
            )

            return jsonify({
                'status': 'success',
                'response': chat_result['new_response'],
                'old_response_summary': chat_result['old_response_summary'],
                'conversation_state': {}
            })

        # === Default Intent ===
        else:
            instruction = (
                "The assistant helps users with school searches and admissions. "
                "If the query is vague or off-topic, ask the user if they need help with finding schools or admissions."
            )
            chat_result = chat_with_history(
                role="School Researcher and Admission Assistant",
                prompt=prompt,
                old_summary=old_summary,
                additional_instructions=instruction
            )

            return jsonify({
                'status': 'success',
                'response': chat_result['new_response'],
                'old_response_summary': chat_result['old_response_summary'],
                'conversation_state': conversation_state
            })
=======
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
>>>>>>> master

    except Exception as e:
        print(f"[Error] {e}")
        return jsonify({
            'status': 'error',
            'response': 'An internal error occurred while processing your request.'
        }), 500
