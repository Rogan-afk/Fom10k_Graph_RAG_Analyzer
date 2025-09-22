import os
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from pyvis.network import Network
from dotenv import load_dotenv

load_dotenv()
os.makedirs("graphs", exist_ok=True)

graph_prompt = ChatPromptTemplate.from_messages(
    [(
        "system",
        """
        You are an expert financial analyst creating a knowledge graph from a 10-K filing.
        Your goal is to extract a detailed and meaningful graph focusing on strategic information.
        - Nodes: Extract key entities like the Company, its Business Segments, Products/Services, specified Financial Metrics (e.g., Total Revenue, Net Income, Segment Revenues), significant Legal Proceedings, and major Risk Factors. Identify key People mentioned in executive roles.
        - Relationships: Create relationships that describe strategic connections. For example:
          - (Company)-[HAS_SEGMENT]->(Business Segment)
          - (Business Segment)-[GENERATES]->(Financial Metric)
          - (Company)-[FACES_RISK]->(Risk Factor)
          - (Company)-[LED_BY]->(Person)
          - (Company)-[INVOLVED_IN]->(Legal Proceeding)
        - Density: Capture a comprehensive set of connections. Aim for a rich graph with roughly 30-60 nodes and up to 200 of the most significant relationships to provide a thorough overview.
        """
    ),
        ("human", "Use the given format to extract information from the following text:\n\n{input}")
    ])


def generate_knowledge_graph(text: str, original_filename: str) -> str:
    """
    Generates an optimized knowledge graph, handling large text via chunking,
    and saves it as a robust, self-contained interactive HTML file.
    """
    if not text or len(text.strip()) < 500:
        raise ValueError("PDF file can't be processed. Please check if the text is selectable and that it's a correctly formatted 10-K file.")

    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    
    graph_transformer = LLMGraphTransformer(llm=llm, prompt=graph_prompt)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=256)
    text_chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in text_chunks]
    
    all_nodes = {}
    all_relationships = []

    print(f"Processing {len(documents)} chunks for the knowledge graph...")
    for i, doc_chunk in enumerate(documents):
        print(f"  - Processing chunk {i+1}/{len(documents)}")
        try:
            graph_document_chunk = graph_transformer.convert_to_graph_documents([doc_chunk])
            for node in graph_document_chunk[0].nodes:
                if node.id not in all_nodes:
                    all_nodes[node.id] = node
            all_relationships.extend(graph_document_chunk[0].relationships)
        except Exception as e:
            print(f"  - Warning: Could not process chunk {i+1}. Error: {e}")
            continue

    print("All chunks processed. Pruning and generating visualization...")
    
    MAX_RELATIONSHIPS = 250 
    if len(all_relationships) > MAX_RELATIONSHIPS:
        print(f"Graph has {len(all_relationships)} relationships. Pruning to the first {MAX_RELATIONSHIPS} for clarity.")
        all_relationships = all_relationships[:MAX_RELATIONSHIPS]

    final_node_ids = set(rel.source.id for rel in all_relationships) | set(rel.target.id for rel in all_relationships)
    final_nodes = {node_id: node for node_id, node in all_nodes.items() if node_id in final_node_ids}

    net = Network(height="100%", width="100%", directed=True, notebook=False, cdn_resources='remote', bgcolor="#222222", font_color="white")
    
    net.set_options("""
    var options = {
      "interaction": { "navigationButtons": true, "keyboard": { "enabled": true } },
      "physics": { "solver": "forceAtlas2Based", "forceAtlas2Based": { "gravitationalConstant": -100, "centralGravity": 0.005, "springLength": 230, "springConstant": 0.18 } }
    }
    """)

    for node_id, node in final_nodes.items():
        net.add_node(node.id, label=node.id, title=f"Type: {node.type}", group=node.type)

    for rel in all_relationships:
        if rel.source.id in final_nodes and rel.target.id in final_nodes:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type)

    graph_output_filename = f"{os.path.splitext(original_filename)[0]}.html"
    graph_path = os.path.join("graphs", graph_output_filename)
    
    net.save_graph(graph_path)
    
    print(f"Graph visualization saved to {graph_path}")
    return graph_path