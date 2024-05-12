# pip install -U langchain-chroma langchain-upstage
from langchain_chroma import Chroma
from langchain_upstage import UpstageEmbeddings, UpstageLayoutAnalysisLoader

# Free API keys for unlimited use. No need to register, just use ‘em!
docai_api_key = "hack-with-upstage-docai-0427"  # For Layout Analyzer
solar_api_key = "hack-with-upstage-solar-0427"  # For everything else

chunks = UpstageLayoutAnalysisLoader(["./crispr.pdf"],
        use_ocr=False, split="element", output_type="text", api_key=docai_api_key
    ).load()  # Should take several minutes
embeddings = UpstageEmbeddings(api_key=solar_api_key)
db = Chroma.from_documents(chunks, embeddings)  # Should take several minutes

query = "What are the future directions of CRISPR?"
docs = db.similarity_search(query)
print(docs[0].page_content)
