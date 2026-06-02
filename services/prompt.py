def build_prompt(readme, metadata):

    # Extract metadata values
    functions = metadata["functions"]
    file_count = metadata["file_count"]

    # Build structured prompt
    prompt = f"""
You are an expert software documentation generator.

Analyze the following project and generate structured documentation.

-------------------------------
README CONTENT:
{readme[:2000]}
-------------------------------

PROJECT METADATA:
- Total Files: {file_count}
- Total Functions: {len(functions)}

Some Functions:
{functions[:50]}

-------------------------------

Generate documentation in the following format:

1. SUMMARY
- Explain what the project does

2. KEY FEATURES
- List main features based on code and README

3. TECHNOLOGIES USED
- Identify languages/frameworks

4. ARCHITECTURE OVERVIEW
- Explain high-level structure

5. IMPORTANT FUNCTIONS
- Highlight key functions and their purpose

-------------------------------

IMPORTANT:
- Keep it clear and professional
- Do not hallucinate unknown details
- Use only provided data
"""

    return prompt
