import os
import re
import torch
import json
from transformers import GPT2LMHeadModel, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

# Config
MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "models/emotion_model_new")
DEFAULT_SPEAKERS = ["Alex", "Taylor"]

def initialize_model(model_path=MODEL_PATH):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        # Load tokenizer - important to use the correct one for your fine-tuned model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Load model
        model = GPT2LMHeadModel.from_pretrained(model_path)
        
        # Ensure tokenizer has all special tokens
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model.to(device)
        model.eval()
        
        return tokenizer, model, device
        
    except Exception as e:
        logger.error(f"Model initialization failed: {str(e)}")
        raise RuntimeError(f"Could not load model from {model_path}. Please verify model files exist.")

# Initialize model at startup
try:
    tokenizer, model, device = initialize_model()
    logger.info("Model and tokenizer loaded successfully")
except RuntimeError as e:
    logger.error(f"Critical error: {str(e)}")
    tokenizer, model, device = None, None, None

GO_EMOTIONS = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring',
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval',
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief',
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization',
    'relief', 'remorse', 'sadness', 'surprise', 'neutral'
]
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