import html

def format_ai_doc(text):

    if not text:
        return "No content generated ❌"

    # Normalize spacing
    text = text.replace("\r", "")

    # Fix HTML encoding (&amp; → &)
    text = html.unescape(text)

    # Remove backticks
    text = text.replace("`", "")

    # Fix multiple spaces
    text = text.replace("  ", " ")

    # Add spacing for sections
    sections = [
        "1. SUMMARY",
        "2. KEY FEATURES",
        "3. TECHNOLOGIES USED",
        "4. ARCHITECTURE OVERVIEW",
        "5. IMPORTANT FUNCTIONS"
    ]

    for section in sections:
        text = text.replace(section, f"\n\n{section}\n")

    # Better bullet formatting
    text = text.replace("- ", "\n  • ")

    # Clean lines
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    return "\n".join(cleaned_lines)