import os
import git
import shutil
from services.storage import upload_file, zip_repo

REPO_FOLDER = "cloned_repo"

def clone_repository(repo_url):

    # Ensure safe cleanup
    if os.path.exists(REPO_FOLDER):
        try:
            shutil.rmtree(REPO_FOLDER)
        except Exception:
            shutil.rmtree(REPO_FOLDER, ignore_errors=True)

    # Fresh clone
    git.Repo.clone_from(repo_url, REPO_FOLDER)
    
    # ZIP repo
    zip_path = zip_repo(REPO_FOLDER)

    # Upload to Azure
    upload_file(zip_path, "repo/repo.zip")

    # CLEAN LOCAL ZIP
    if os.path.exists(zip_path):
        os.remove(zip_path)

    return REPO_FOLDER