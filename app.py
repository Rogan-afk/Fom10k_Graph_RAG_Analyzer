import gradio as gr
import os
from dotenv import load_dotenv
import time
import threading
from queue import Queue
from flask import Flask, send_from_directory

# Import local modules
from src.file_manager import list_uploaded_files, save_uploaded_file, get_file_path, delete_file_and_artifacts
from src.text_processor import process_pdf_to_text
from src.knowledge_graph_generator import generate_knowledge_graph
from src.graph_rag import GraphRAG

load_dotenv()

# --- Application Setup ---
os.makedirs("uploads", exist_ok=True)
os.makedirs("graphs", exist_ok=True)
os.makedirs("processed_texts", exist_ok=True)
rag_chain = GraphRAG()

# --- Flask Server for Serving Graphs ---
GRAPH_SERVER_PORT = 7861
flask_app = Flask(__name__)

@flask_app.route('/graphs/<path:filename>')
def serve_graph(filename):
    return send_from_directory('graphs', filename)

def run_flask():
    flask_app.run(host='0.0.0.0', port=GRAPH_SERVER_PORT, debug=False)

# --- Backend Tasks ---

def _generation_task(filename: str, queue: Queue):
    """Core task running in a separate thread to prevent UI freezing."""
    try:
        queue.put(("progress", (0.1, "Analyzing document structure...")))
        pdf_path = get_file_path(filename)
        text, txt_path = process_pdf_to_text(pdf_path)
        
        queue.put(("progress", (0.4, "Generating knowledge graph from key sections...")))
        graph_html_path = generate_knowledge_graph(text, filename)
        
        queue.put(("progress", (0.9, "Preparing graph for analysis...")))
        rag_chain.load_graph(filename)
        
        queue.put(("complete", (graph_html_path, f"Successfully processed {filename}.", filename)))

    except ValueError as ve:
        queue.put(("error", str(ve)))
    except Exception as e:
        queue.put(("error", f"An unexpected error occurred: {str(e)}"))

def process_document(filename, progress=gr.Progress(track_tqdm=True)):
    """Main function to process a document. Implements caching and threading."""
    if not filename:
        yield None, "Please select a document.", None
        return

    base_name = os.path.splitext(filename)[0]
    graph_html_path = os.path.join("graphs", f"{base_name}.html")
    txt_path = os.path.join("processed_texts", f"{base_name}.txt")

    if os.path.exists(graph_html_path) and os.path.exists(txt_path):
        progress(1, desc="Loading from cache...")
        rag_chain.load_graph(filename)
        yield load_visualization_from_file(filename), f"Loaded cached results for {filename}.", filename
        return
        
    result_queue = Queue()
    thread = threading.Thread(target=_generation_task, args=(filename, result_queue))
    thread.start()

    while thread.is_alive() or not result_queue.empty():
        try:
            item = result_queue.get(timeout=0.1)
            msg_type, data = item
            if msg_type == "progress":
                progress(data[0], desc=data[1])
                yield None, data[1], None
            elif msg_type == "error":
                yield f"<h3>Error</h3><p>{data}</p>", data, None
                return
            elif msg_type == "complete":
                progress(1, desc="Processing Complete!")
                yield load_visualization_from_file(data[2]), data[1], data[2]
                return
        except Exception:
            yield None, "Processing...", None
            time.sleep(0.2)

def handle_file_upload(file_obj, all_files_state):
    """Handles file upload and updates UI elements."""
    if file_obj:
        new_path = save_uploaded_file(file_obj)
        updated_files = list_uploaded_files()
        filename = os.path.basename(new_path)
        return gr.Dropdown(choices=updated_files, value=filename), gr.Dropdown(choices=updated_files, value=filename), gr.Dropdown(choices=updated_files, value=filename), updated_files
    return gr.Dropdown(choices=all_files_state), gr.Dropdown(choices=all_files_state), gr.Dropdown(choices=all_files_state), all_files_state

def handle_delete_file(filename_to_delete):
    """Deletes a file and all its associated artifacts, then refreshes the UI."""
    if not filename_to_delete:
        return list_uploaded_files(), "Please select a file to delete.", gr.Dropdown(choices=list_uploaded_files()), gr.Dropdown(choices=list_uploaded_files()), gr.Dropdown(choices=list_uploaded_files()), "<h3>Select a document to view.</h3>"
    
    status = delete_file_and_artifacts(filename_to_delete)
    updated_files = list_uploaded_files()
    
    return updated_files, status, gr.Dropdown(choices=updated_files, value=None), gr.Dropdown(choices=updated_files, value=None), gr.Dropdown(choices=updated_files, value=None), "<h3>Select a document to view.</h3>"

def handle_chat_interaction(filename, question, history):
    """Manages the RAG chat conversation."""
    if not filename:
        history.append((question, "A data source must be selected for querying."))
        return history, ""
    if not rag_chain.is_graph_loaded(filename):
        history.append((question, "The selected document has not been processed. Please process it first."))
        return history, ""
    response = rag_chain.query(filename, question)
    history.append((question, response))
    return history, ""

def load_visualization_from_file(filename):
    """Returns an iframe pointing to the served HTML graph file."""
    if not filename:
        return "<h3>Select a processed document to view its knowledge graph.</h3>"
    
    graph_filename = f"{os.path.splitext(filename)[0]}.html"
    graph_path = os.path.join("graphs", graph_filename)

    if os.path.exists(graph_path):
        iframe_src = f"http://127.0.0.1:{GRAPH_SERVER_PORT}/graphs/{graph_filename}"
        return f'<iframe src="{iframe_src}" width="100%" height="100%"></iframe>'
    
    return f"<h3>Graph not found for '{filename}'.</h3><p>Please process the document first.</p>"

# --- Gradio User Interface ---
with gr.Blocks(theme=gr.themes.Default(), css="static/styles.css") as demo:
    gr.Markdown("# Form10k_Graph_RAG_Analyzer")
    gr.Markdown("An enterprise tool for converting SEC 10-K filings into queryable knowledge graphs.")
    all_files = gr.State(list_uploaded_files())
    
    with gr.Tabs() as tabs:
        with gr.TabItem("1. Document Processing", id=0):
            with gr.Row():
                with gr.Column(scale=1):
                    file_uploader = gr.File(label="Upload 10-K Filing (PDF, max 200MB)", file_types=[".pdf"])
                    file_dropdown_manage = gr.Dropdown(choices=all_files.value, label="Select Document")
                    with gr.Row():
                        process_button = gr.Button("Process Document", variant="primary", scale=2)
                        delete_button = gr.Button("Delete", variant="stop", scale=1)
                with gr.Column(scale=2):
                    gr.Markdown("### Process Log")
                    process_status = gr.Textbox(label="System Status", interactive=False)

        with gr.TabItem("2. Query & Analysis", id=1):
            with gr.Column():
                file_dropdown_chat = gr.Dropdown(choices=all_files.value, label="Select Data Source")
                chatbot = gr.Chatbot(label="Analysis Chat", height=550, bubble_full_width=False)
                msg_textbox = gr.Textbox(label="Enter Query:", placeholder="Example: 'Summarize the main risk factors.'")
                msg_textbox.submit(handle_chat_interaction, [file_dropdown_chat, msg_textbox, chatbot], [chatbot, msg_textbox])
                gr.ClearButton([msg_textbox, chatbot], value="Clear Session")
        
        with gr.TabItem("3. Graph Visualization", id=2):
            file_dropdown_visualize = gr.Dropdown(choices=all_files.value, label="Select Graph to Display")
            graph_html_display = gr.HTML("<h3>Select a processed document to view its knowledge graph.</h3>", elem_id="graph-display")

    # --- Event Handling ---
    file_uploader.upload(handle_file_upload, [file_uploader, all_files], [file_dropdown_manage, file_dropdown_visualize, file_dropdown_chat, all_files])
    
    process_button.click(
        fn=process_document, 
        inputs=[file_dropdown_manage], 
        outputs=[graph_html_display, process_status, file_dropdown_visualize]
    ).then(
        fn=lambda x: gr.Tabs(selected=2) if x is not None else gr.Tabs(),
        inputs=[file_dropdown_visualize], outputs=[tabs]
    )

    delete_button.click(
        fn=handle_delete_file,
        inputs=[file_dropdown_manage],
        outputs=[all_files, process_status, file_dropdown_manage, file_dropdown_chat, file_dropdown_visualize, graph_html_display]
    )
    
    file_dropdown_visualize.change(load_visualization_from_file, [file_dropdown_visualize], [graph_html_display])

if __name__ == "__main__":
    # Start the Flask server in a daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Launch the Gradio app
    demo.launch(max_file_size="200mb")
