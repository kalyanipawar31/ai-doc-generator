import re
import os
import json
from services.storage import upload_file
from services.db import create_connection, create_table

def extract_functions(file_paths):
    functions = []

    for file in file_paths:
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Python functions
                py_funcs = re.findall(r"def (\w+)\(", content)

                # JS functions
                js_funcs = re.findall(r"function (\w+)\(", content)

                functions.extend(py_funcs + js_funcs)

        except:
            continue

    # remove duplicates
    functions = list(set(functions))

    metadata = {
        "functions": functions,
        "file_count": len(file_paths)
    }

    create_table()

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metadata (file_count, functions)
        VALUES (?, ?)
    """, (
        metadata["file_count"],
        json.dumps(metadata["functions"])   # store list as string
    ))

    conn.commit()
    conn.close()

    # ensure folder exists
    storage_path = os.path.join("storage", "metadata")
    os.makedirs(storage_path, exist_ok=True)

    # save metadata (only once )
    file_path = os.path.join(storage_path, "metadata.json")
    with open(file_path, "w") as f:
        json.dump(metadata, f, indent=4)
    
    upload_file(file_path, "metadata/metadata.json")

    print("Parser completed", flush=True)
    print("Total functions extracted:", len(functions), flush=True)

    return functions
