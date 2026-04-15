# Sigiri Ayu RAG Chatbot 🌿

A Streamlit-based RAG chatbot for the **Sigiri Ayu** Ayurvedic beauty brand. The bot walks the user through a short questionnaire, recommends products with matching images, and answers any follow-up questions about products or the brand — all grounded in the provided brand and product files.

## Features

- **Guided questionnaire** (3 quick questions → personalized product recommendations)
- **Free-form chat** grounded in brand + 24 product descriptions
- **Session memory** for natural follow-ups
- **Mascot** with reactive speech bubble per conversation state
- **Mobile-responsive**, white, modern UI
- **Optimized for Streamlit Community Cloud free tier** (small deps, cached embeddings, lightweight retrieval)

## Stack

| Layer | Choice |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini 1.5 Flash |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Vector store | In-memory numpy (~28 chunks — no FAISS / Chroma needed) |
| Orchestration | Plain Python (no LangChain) |

## Setup

Requires **Python 3.10**.

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root (already present in this project):

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Run locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

On first launch, the embedding model downloads (~90 MB) and the corpus is embedded and cached to `data/embeddings_cache.pkl`. Subsequent runs are instant.

## Run tests

```bash
pytest tests/ -v
```

Tests cover:
- **`test_data_loader.py`** — parses all 24 products and the brand chunks
- **`test_image_matcher.py`** — every product has a matching image on disk
- **`test_retriever.py`** — semantic retrieval quality for realistic queries
- **`test_chat_flow.py`** — questionnaire state machine + mocked RAG chain end-to-end

Gemini calls in tests are **mocked** — no live API hits.

## Manual golden-path smoke test

1. `streamlit run app.py`
2. Mascot loads and animates at the top
3. Click **Get a recommendation** → Hair Care → Dandruff → Oily
4. Assistant returns product cards with images visible
5. Ask "What ingredients are in the shampoo?" in free chat — grounded answer
6. Ask "Tell me about the Sigiri Ayu brand" — brand-grounded answer
7. Ask "Do you sell shoes?" — polite out-of-scope response
8. Resize browser to mobile width — layout reflows

## Deploy to Streamlit Community Cloud

1. Push this project to a **public GitHub repo** (make sure `.env` is gitignored — it is).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, and pick `app.py` as the entry point.
3. In the Streamlit Cloud app settings → **Secrets**, add:
   ```
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
4. Deploy. First cold start takes ~45 s while `sentence-transformers` downloads the model; subsequent loads are fast thanks to `@st.cache_resource`.

## Project layout

```
madhusa RAG/
├── app.py                          # Streamlit entry point
├── src/
│   ├── data_loader.py              # Brand + product parsing into Chunks
│   ├── embeddings.py               # Local ST embedder + on-disk cache
│   ├── retriever.py                # Cosine-similarity top-k
│   ├── rag_chain.py                # Gemini prompt + product-name extraction
│   ├── chat_flow.py                # Questionnaire state machine
│   ├── image_matcher.py            # Product name → image path
│   └── ui.py                       # CSS, mascot, message & card renderers
├── tests/                          # pytest suite
├── data/embeddings_cache.pkl       # Generated on first run (gitignored)
├── .streamlit/config.toml          # White theme, collapsed sidebar
├── Images/                         # 24 product .jpeg files (filename = product name)
├── Mascot/                         # mascot_image.png + Mascot Animation.webm
├── Sigiri_Ayu_Details              # Brand overview (plain text)
├── Sigiri_Ayu_Product_Descriptions.md  # 24 structured product descriptions
└── requirements.txt
```
