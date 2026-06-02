
import re

def format_ai_doc(ai_text):

    # Remove markdown bold symbols
    ai_text = ai_text.replace("**", "")

    # Add spacing before sections
    ai_text = re.sub(r'(1\. Summary)', r'\1', ai_text)
    ai_text = re.sub(r'(2\. Key Features)', r'\n\1', ai_text)
    ai_text = re.sub(r'(3\. Technologies Used)', r'\n\1', ai_text)

    # Convert headings to uppercase
    ai_text = ai_text.replace("1. Summary", "1. SUMMARY")
    ai_text = ai_text.replace("2. Key Features", "2. KEY FEATURES")
    ai_text = ai_text.replace("3. Technologies Used", "3. TECHNOLOGIES USED")

    return ai_text
