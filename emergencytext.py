import random

def generate_emergency_text():
    # Lists of phrases for different emergency scenarios with skin
    burn_phrases = ["Apply cool water to the burn.", "Cover the burn with a clean cloth.", "Seek medical attention for severe burns."]
    cut_phrases = ["Clean the cut with mild soap and water.", "Apply an antiseptic ointment.", "Use a sterile bandage to cover the cut."]
    rash_phrases = ["Avoid scratching the rash.", "Apply a soothing lotion.", "Consult a healthcare professional if the rash persists."]

    # Randomly choose an emergency scenario
    emergency_type = random.choice(["Burn", "Cut", "Rash"])

    # Select phrases based on the chosen emergency type
    if emergency_type == "Burn":
        emergency_text = random.choice(burn_phrases)
    elif emergency_type == "Cut":
        emergency_text = random.choice(cut_phrases)
    elif emergency_type == "Rash":
        emergency_text = random.choice(rash_phrases)
    else:
        emergency_text = "No specific emergency information available."

    return f"Emergency for skin: {emergency_type}\n{emergency_text}"

# Example usage
emergency_text = generate_emergency_text()
print(emergency_text)