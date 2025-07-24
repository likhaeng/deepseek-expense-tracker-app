# Deepseek AI online question sampling
## Prompt
    # Here is the company nature of business
    # 1. IMPORT & EXPORT RAW MATERIAL FOR MEDICAL USE 
    # 2. OPERATING WELLNESS AND HEALTH CONSULTATION 
    # 3. DISTRIBUTION AND TRADING OF RAW MATERIALS AND PRODUCT FOR MEDICAL USE

    # Product of the company includes:
    # 1. Antioxidants
    # 2. Anti sugar

    # Service of the company includes:
    # 1. Beauty & Health
    # 2. Branding & Design

    # Based on this, please generate a list of question that could be raised by their doctor using an chat AI application
## Response
    # Here’s a list of potential questions that doctors (or healthcare professionals) might ask via a chat AI application related to i-actions.com’s business in medical raw materials, wellness, and health products:

        # 1. Product-Specific Questions
            # Antioxidants
                # What are the clinically proven benefits of your antioxidant raw materials?
                # Are your antioxidants derived from natural or synthetic sources?
                # Do you have third-party lab test results (e.g., HPLC, GC-MS) for purity and potency?
                # What is the recommended dosage for integrating your antioxidants into supplements?
                # Are there any known drug interactions with your antioxidant compounds?

            # Anti-Sugar (Glycation Inhibitors)
                # How do your anti-sugar compounds work to inhibit glycation in the body?
                # Can you provide research or clinical studies supporting efficacy?
                # Are your anti-sugar ingredients suitable for diabetic patients?
                # What is the bioavailability of your anti-sugar raw materials?

        # 2. Regulatory & Safety Questions
            # Are your raw materials GMP-certified or compliant with USP/EP/JP standards?
            # Do you provide Certificate of Analysis (CoA) for each batch?
            # Are your ingredients FDA-approved or EU-compliant (EFSA, EMA)?
            # Have your products undergone toxicity or allergen testing?
            # Are there any side effects or contraindications for long-term use?

        # 3. Application & Formulation Support
            # Can your raw materials be used in capsules, tablets, or topical formulations?
            # Do you offer custom blending for specific health formulations?
            # What excipients or stabilizers are recommended for your active ingredients?
            # Do you provide white-labeling or private-label services for finished products?

        # 4. Supply Chain & Business Logistics
            # What is your minimum order quantity (MOQ) for raw materials?
            # Do you offer global shipping, and what are the lead times?
            # Are your raw materials temperature-sensitive (require cold chain logistics)?
            # Can you provide samples for testing before bulk orders?

        # 5. Wellness & Health Consultation
            # Do you offer scientific dossiers or medical education materials for doctors?
            # Can your team assist in clinical protocol design for studies using your ingredients?
            # Are there patient education resources (e.g., pamphlets, videos) available?

        # 6. AI Chat-Specific Queries
            # Can this AI tool provide real-time product comparisons (e.g., antioxidants vs. competitors)?
            # Is there a database of research papers linked to your ingredients?
            # Can I request a personalized recommendation based on patient health profiles?

    # Suggested Next Steps for i-actions.com’s AI Chat
        # Integrate a medical knowledge base (studies, CoAs, FAQs).
        # Enable document uploads (e.g., lab reports for analysis).
        # Offer multi-language support (if targeting global doctors).
        # Would you like me to refine this for a specific medical specialty (e.g., dermatology, endocrinology)?

import os
import requests
from bs4 import BeautifulSoup
from pymed import PubMed
import arxiv
from ollama import Client  # Ollama Python client

# Initialize Ollama client (running locally)
client = Client(host='http://localhost:11434')

# --- PubMed Search Function (Same as Before) ---
def search_pubmed(query, max_results=3):
    pubmed = PubMed(tool="MyRAGApp", email="likhaeng@blueoceanit.com.my")
    results = pubmed.query(query, max_results=max_results)
    articles = []
    for article in results:
        article_data = {
            "title": article.title,
            "abstract": article.abstract,
            "doi": article.doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{article.pubmed_id}/",
            "authors": ", ".join([author["lastname"] for author in article.authors]),
            "journal": article.journal,
            "year": article.publication_date.year if article.publication_date else None,
        }
        articles.append(article_data)
    return articles

# --- ArXiv Search (Same as Before) ---
def search_arxiv(query, max_results=3):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    articles = []
    for result in search.results():
        articles.append({
            "title": result.title,
            "url": result.entry_id,
            "abstract": result.summary,
            "authors": ", ".join([author.name for author in result.authors]),
        })
    return articles

# --- Generate Response Using Ollama (DeepSeek R1) ---
def generate_ollama_response(query, context):
    prompt = f"""
    Question: {query}
    Context: {context}
    Answer the question truthfully based on the provided articles. Cite references like [1], [2], etc.
    """
    
    response = client.generate(
        model='deepseek-r1:7b',  # Use the correct model name in Ollama
        prompt=prompt,
        system="You are a helpful scientific assistant. Use the provided articles to answer.",
    )
    return response['response']

# --- RAG Pipeline with Ollama ---
def generate_rag_response(query, sources="pubmed"):
    # Step 1: Retrieve relevant articles
    if sources == "pubmed":
        articles = search_pubmed(query)
    elif sources == "arxiv":
        articles = search_arxiv(query)
    else:
        raise ValueError("Supported sources: 'pubmed', 'arxiv'")

    if not articles:
        return "No relevant articles found."

    # Step 2: Format context with references
    context = ""
    references = []
    for i, article in enumerate(articles):
        context += f"Article {i+1}: {article['title']}\nAbstract: {article.get('abstract', 'N/A')}\n\n"
        references.append(f"[{i+1}] {article['title']} - {article['url']}")

    # Step 3: Generate answer using Ollama (DeepSeek R1)
    answer = generate_ollama_response(query, context)
    answer_with_refs = f"{answer}\n\nReferences:\n" + "\n".join(references)
    return answer_with_refs

# --- Example Usage ---
if __name__ == "__main__":
    query = "Effect of consuming hydrogen rich substance"
    print("Searching PubMed and generating answer with Ollama (DeepSeek R1)...")
    response = generate_rag_response(query, sources="pubmed")
    print(response)