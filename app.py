from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
from git import Repo
import os
import shutil
from services.ingestion import clone_repository
from services.scanner import scan_repository
from services.parser import extract_functions
from services.prompt import build_prompt
from services.llm import call_llm
from services.docgen import format_ai_doc


app = Flask(__name__)
CORS(app)

REPO_FOLDER = "cloned_repo"

@app.route("/")
def home():
    return "Backend running"

# Clone Repository 
@app.route("/clone-repo", methods=["POST"])
def clone_repo():
    data = request.get_json()
    repo_url = data.get("repoUrl")

    try:
        repo_path = clone_repository(repo_url)

        return jsonify({
            "status": "success",
            "message": "Repository cloned successfully",
            "path": repo_path
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
    
# Read README
@app.route("/read-file", methods=["GET"])
def read_file():
    import re
    import html

    try:
        readme_content = ""

        # Find README file
        for file in os.listdir(REPO_FOLDER):
            if "readme" in file.lower():

                file_path = os.path.join(REPO_FOLDER, file)

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()

                break

        # If not found
        if readme_content == "":
            return jsonify({
                "status": "error",
                "message": "README not found"
            })

        # CLEANING (required in architecture — usable content)
        readme_content = re.sub(r'!\[.*?\]\(.*?\)', '', readme_content)
        readme_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', readme_content)
        readme_content = re.sub(r'<.*?>', '', readme_content)
        readme_content = re.sub(r'\[.*?\]:\s*https?://\S+', '', readme_content)
        readme_content = re.sub(r'[#`*>]', '', readme_content)
        readme_content = re.sub(r'\n\s*\n', '\n\n', readme_content)
        readme_content = html.unescape(readme_content)

        return jsonify({
            "status": "success",
            "content": readme_content
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# Scanner Test
@app.route("/scan-repo", methods=["GET"])
def scan_repo():
    try:
        files = scan_repository(REPO_FOLDER)

        return jsonify({
            "status": "success",
            "total_files": len(files),
            "files": files[:20]   # show first 20 only
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# Parser Trigger
@app.route("/parse-repo", methods=["GET"])
def parse_repo():
    try:
        # Step 1: scan repository
        files = scan_repository(REPO_FOLDER)

        # Step 2: extract functions + create metadata.json
        functions = extract_functions(files)

        return jsonify({
            "status": "success",
            "total_functions": len(functions),
            "functions": functions[:50]  # show only first 50
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route("/ai-doc", methods=["GET"])
def ai_doc():
    import json
    from services.db import create_connection

    try:
        # Step 1: scan repository
        files = scan_repository(REPO_FOLDER)

        # Step 2: run parser → creates metadata.json
        extract_functions(files)

        # Step 3: load metadata
        file_path = os.path.join("storage", "metadata", "metadata.json")

        if not os.path.exists(file_path):
            return jsonify({
                    "status": "error",
                    "message": "Metadata not found ❌ Run Analyze first"
                })
        
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_count, functions FROM metadata ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        conn.close()
        
        metadata = {
            "file_count": row[0],
            "functions": json.loads(row[1])
        }
        
        # Step 4: read README
        readme = ""
        for file in os.listdir(REPO_FOLDER):
            if "readme" in file.lower():
                with open(os.path.join(REPO_FOLDER, file), "r", encoding="utf-8", errors="ignore") as f:
                    readme = f.read()
                break

        # Step 5: build prompt
        prompt = build_prompt(readme, metadata)

        # Step 6: call LLM
        ai_output = call_llm(prompt)

        if not ai_output:
            return jsonify({
                "status": "error",
                "aiDoc": "⚠️ AI not available. Please try again."
            })

        # Step 7: format output
        final_doc = format_ai_doc(ai_output)

        return jsonify({
            "status": "success",
            "aiDoc": final_doc
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        })


@app.route("/generate-doc", methods=["GET"])
def generate_doc():
    import re
    import html

    try:
        readme_content = ""

        # ✅ Step 1: Read README
        for file in os.listdir(REPO_FOLDER):
            if "readme" in file.lower():
                file_path = os.path.join(REPO_FOLDER, file)

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()
                break

        if readme_content == "":
            return jsonify({
                "status": "error",
                "message": "README not found"
            })

        # ✅ Step 2: Clean content
        readme_content = re.sub(r'!\[.*?\]\(.*?\)', '', readme_content)
        readme_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', readme_content)
        readme_content = re.sub(r'<.*?>', '', readme_content)
        readme_content = re.sub(r'\[.*?\]:\s*https?://\S+', '', readme_content)
        readme_content = re.sub(r'[#`*>]', '', readme_content)
        readme_content = html.unescape(readme_content)
        readme_content = re.sub(r'\n\s*\n', '\n\n', readme_content)

        # ✅ Step 3: Remove first line if single word (like “Flask”)
        lines = readme_content.split("\n")
        if len(lines) > 0 and len(lines[0].strip().split()) == 1:
            lines = lines[1:]
        clean_content = "\n".join(lines)

        # ✅ Step 4: Build doc
        doc = f"""PROJECT DOCUMENTATION
------------------------------------

Description:
{clean_content[:1500]}

------------------------------------

Summary:
Generated from repository README
"""

        return jsonify({
            "status": "success",
            "documentation": doc
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
    
# Download PDF API
@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from services.storage import upload_file

    try:
        data = request.get_json()
        content = data.get("content", "")

        os.makedirs("storage/documents", exist_ok=True)
        file_path = "storage/documents/output.pdf"

        c = canvas.Canvas(file_path, pagesize=letter)
        text = c.beginText(40, 750)
        text.setFont("Helvetica", 10)

        upload_file(file_path, "documents/output.pdf")

        # Add line by line text
        from textwrap import wrap
        
        text = c.beginText(40, 750)
        text.setFont("Helvetica", 10)
        line_height = 14  # proper spacing
        
        y_position = 750
        
        for line in content.split("\n"):
        
            if line.strip() == "":
                y_position -= line_height  # paragraph gap
                continue
            
            wrapped_lines = wrap(line, 90)
        
            for wline in wrapped_lines:
                # CHECK BEFORE WRITING
                if y_position < 50:
                    c.drawText(text)
                    c.showPage()
        
                    text = c.beginText(40, 750)
                    text.setFont("Helvetica", 10)
                    y_position = 750
        
                text.setTextOrigin(40, y_position)
                text.textLine(wline)
        
                y_position -= line_height  # move down properly
        
        # FINAL DRAW
        c.drawText(text)
        c.save()

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})    

# Download Word API
@app.route("/download-word", methods=["POST"])
def download_word():
    from docx import Document
    from services.storage import upload_file

    try:
        data = request.get_json()
        content = data.get("content", "")

        doc = Document()

        for line in content.split("\n"):
            doc.add_paragraph(line)

        os.makedirs("storage/documents", exist_ok=True)
        file_path = "storage/documents/output.docx"

        doc.save(file_path)

        upload_file(file_path, "documents/output.docx")

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ZIP upload
@app.route("/upload-zip", methods=["POST"])
def upload_zip():
    import zipfile

    try:
        file = request.files["file"]

        if not file:
            return jsonify({"status": "error", "message": "No file uploaded"})

        # Remove folder safely
        if os.path.exists(REPO_FOLDER):
            shutil.rmtree(REPO_FOLDER, ignore_errors=True)

        # Save zip file
        zip_path = "uploaded_repo.zip"
        file.save(zip_path)

        # Extract safely
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(REPO_FOLDER)

        return jsonify({
            "status": "success",
            "message": "ZIP uploaded and extracted"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# Upload Folder API
@app.route("/upload-folder", methods=["POST"])
def upload_folder():
    try:
        import shutil

        files = request.files.getlist("files")

        if not files:
            return jsonify({
                "status": "error",
                "message": "No files uploaded"
            })

        # Clean existing repo
        if os.path.exists(REPO_FOLDER):
            shutil.rmtree(REPO_FOLDER, ignore_errors=True)

        os.makedirs(REPO_FOLDER, exist_ok=True)

        # Save all files preserving structure
        for file in files:
            file_path = os.path.join(REPO_FOLDER, file.filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

        return jsonify({
            "status": "success",
            "message": "Folder uploaded successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(port=5001, debug=True)


