from rest_framework.decorators import api_view
from django.http import JsonResponse
import logging
import re
import torch
from transformers import GPT2LMHeadModel, AutoTokenizer
import os

logger = logging.getLogger(__name__)

# Model configuration
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'emotion_model_new')

# Initialize model and tokenizer
try:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = GPT2LMHeadModel.from_pretrained(MODEL_PATH).to(device)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    logger.info("Model and tokenizer loaded successfully")
except Exception as e:
    logger.error(f"Model initialization failed: {str(e)}")
    tokenizer, model, device = None, None, None

def generate_dialogue(
    prompt,
    emotion="neutral",
    num_exchanges=3,  # Reduced for better quality
    max_turn_length=50,
    temperature=0.7,
    top_k=40,
    top_p=0.85,
    repetition_penalty=1.5,
):
    if not tokenizer or not model:
        return "Error: Model not initialized"

    speakers = ["Alex", "Taylor"]
    dialogue = [f"{speakers[0]}: {prompt}"]

    # Enhanced generation template
    generation_template = """Generate natural, realistic dialogue between Alex and Taylor.
    Current mood: {emotion}
    Guidelines:
    - Keep responses to 1 short sentence
    - Stay on topic
    - Maintain natural conversation flow
    - Avoid repetition
    
    Current dialogue:
    {history}
    {next_speaker}:"""

    for exchange in range(num_exchanges):
        for speaker_idx in [1, 0]:  # Alternate speakers
            current_speaker = speakers[speaker_idx]
            
            # Use last 2 exchanges for context
            history = "\n".join(dialogue[-4:]) if len(dialogue) > 1 else dialogue[0]
            
            current_prompt = generation_template.format(
                emotion=emotion,
                history=history,
                next_speaker=current_speaker
            )

            inputs = tokenizer(
                current_prompt,
                return_tensors="pt",
                max_length=256,
                truncation=True,
                padding='max_length'
            ).to(device)

            # Generate with tighter constraints
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=max_turn_length,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=4,
            )

            # Clean and validate response
            generated = tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            # Enhanced cleaning pipeline
            generated = (
                generated.split('.')[0]  # Take first complete sentence
                .split('?')[0]
                .split('!')[0]
                .strip()
                .replace('"', '')
                .replace('--', ',')  # Convert dashes to commas
                .replace('\n', ' ')
            )
            
            # Skip if response is too short or doesn't make sense
            if not generated or len(generated.split()) < 2:
                generated = "..."  # Fallback response
                
            dialogue.append(f"{current_speaker}: {generated}")

    # Final quality check and formatting
    cleaned_dialogue = []
    for line in dialogue[:2*num_exchanges+1]:  # Ensure exact number of turns
        if ':' in line:
            speaker, content = line.split(':', 1)
            cleaned_dialogue.append(f"{speaker.strip()}:{content.strip()}")
    
    return "\n".join(cleaned_dialogue) or "Could not generate valid dialogue"

@api_view(["POST"])
def generate_script(request):
    try:
        data = request.data
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return JsonResponse({"error": "Prompt cannot be empty"}, status=400)

        # Validate parameters with proper ranges
        try:
            emotion = data.get("emotion", "neutral")
            num_exchanges = min(int(data.get("num_exchanges", 3)), 5)  # Max 5 exchanges
            num_exchanges = max(num_exchanges, 1)  # Min 1 exchange
            max_turn_length = min(int(data.get("max_turn_length", 50)), 80)
            max_turn_length = max(max_turn_length, 20)
            temperature = min(float(data.get("temperature", 0.7)), 1.0)
            temperature = max(temperature, 0.1)
            top_k = min(int(data.get("top_k", 40)), 100)
            top_k = max(top_k, 10)
            top_p = min(float(data.get("top_p", 0.85)), 1.0)
            top_p = max(top_p, 0.5)
            repetition_penalty = min(float(data.get("repetition_penalty", 1.5)), 2.0)
            repetition_penalty = max(repetition_penalty, 1.0)
        except (ValueError, TypeError) as e:
            return JsonResponse({"error": f"Invalid parameter: {str(e)}"}, status=400)

        # Generate the dialogue
        generated_text = generate_dialogue(
            prompt=prompt,
            emotion=emotion,
            num_exchanges=num_exchanges,
            max_turn_length=max_turn_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )

        # Final sanitization
        generated_text = re.sub(r'\s+', ' ', generated_text).strip()[:2000]
        
        return JsonResponse({
            "generated_text": generated_text,
            "parameters": {
                "emotion": emotion,
                "num_exchanges": num_exchanges,
                "max_turn_length": max_turn_length,
                "temperature": temperature
            }
        })
    
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return JsonResponse({"error": "Failed to generate dialogue. Please try again."}, status=500)