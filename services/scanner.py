import os

# Define allowed file types to scan
VALID_EXTENSIONS = (".py", ".js", ".ts", ".json", ".md")

def scan_repository(repo_path):
    files = []

    # Walk through all folders recursively
    for root, dirs, filenames in os.walk(repo_path):

        # Skip unwanted directories (not useful for analysis)
        if ".git" in root or "node_modules" in root:
            continue

        # Loop through all files in current folder
        for file in filenames:

            # Check if file type is relevant
            if file.endswith(VALID_EXTENSIONS):

                # Build full file path
                file_path = os.path.join(root, file)

                # Add to results
                files.append(file_path)

    # Return all valid files
    return files
