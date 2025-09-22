import os
import shutil

UPLOAD_DIR = "uploads"
TEXT_DIR = "processed_texts"
GRAPH_DIR = "graphs"

def save_uploaded_file(file_obj):
    """Saves an uploaded file to the designated directory."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    
    file_path = os.path.join(UPLOAD_DIR, os.path.basename(file_obj.name))
    shutil.copyfile(file_obj.name, file_path)
    return file_path

def list_uploaded_files():
    """Returns a list of filenames in the upload directory."""
    if not os.path.exists(UPLOAD_DIR):
        return []
    return [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and not f.startswith('.')]

def get_file_path(filename):
    """Constructs the full path for a given filename."""
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return path
    return None

def delete_file_and_artifacts(filename: str) -> str:
    """Deletes the source PDF, its processed text file, and its graph HTML file."""
    if not filename:
        return "No file selected."
        
    base_name = os.path.splitext(filename)[0]
    
    pdf_path = os.path.join(UPLOAD_DIR, f"{base_name}.pdf")
    txt_path = os.path.join(TEXT_DIR, f"{base_name}.txt")
    graph_path = os.path.join(GRAPH_DIR, f"{base_name}.html")
    
    files_to_delete = [pdf_path, txt_path, graph_path]
    deleted_files = []
    
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
            return f"Error during deletion of {os.path.basename(file_path)}."

    if deleted_files:
        return f"Successfully deleted '{filename}' and its associated cache files."
    else:
        return f"No files found to delete for '{filename}'."