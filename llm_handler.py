#isme llm ka configuration hora hai
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# --- Configuration ---
MODEL_NAME = "google/gemma-2b-it"

def load_model():
    """
    Loads the tokenizer and model from Hugging Face.
    This function will automatically download the model files on the first run.
    """
    print(f"Loading model: {MODEL_NAME}...")

    # The tokenizer converts text into a format the model can understand (tokens)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Check if a GPU is available and set the device accordingly
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load the model with optimizations
    # torch.bfloat16 is used for memory efficiency
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
    ).to(device)

    print("Model and tokenizer loaded successfully.")
    return model, tokenizer, device

def generate_text(model, tokenizer, device, prompt):
    """
    Generates text using the loaded model and tokenizer.
    """
    print("Generating text...")
    
    # The chat template formats the prompt for the model
    chat = [
        {"role": "user", "content": prompt},
    ]
    formatted_prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    
    # Convert the formatted prompt to tokens and send to the active device (CPU or GPU)
    inputs = tokenizer.encode(formatted_prompt, add_special_tokens=False, return_tensors="pt").to(device)
    
    # Generate the response
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs,
            max_new_tokens=250,  # Limit the length of the response
        )
    
    # Decode the generated tokens back into a string
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the model's response part
    model_response = response_text[len(formatted_prompt):].strip()
    
    print("Text generation complete.")
    return model_response

# --- Main Execution Block for Testing ---
if __name__ == "__main__":
    # This block allows you to test this script directly
    model, tokenizer, device = load_model()
    
    # A simple test prompt
    test_prompt = "Write a short, professional follow-up email to a customer who recently purchased a new software product."
    
    print("\n--- Test Prompt ---")
    print(test_prompt)
    
    # Generate the response
    generated_email = generate_text(model, tokenizer, device, test_prompt)
    
    print("\n--- Generated Email ---")
    print(generated_email)