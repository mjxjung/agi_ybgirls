# agi_ybgirls

## Project Overview  
A RAG-based AI medical assistant service that reduces the burden of nurses by handling inquiries before actual consultations.

---

## Installation & Usage

### 📄 Upstage Parsing API & Preprocessing
1. Add your API key to the `.env` file  
2. Run the Document Parsing API:  
   ```bash
   python api/doc_parse/doc_parsing.py
   ```
3. Preprocess the parsed data  
4. Run the preprocessing script:  
   ```bash
   python api/crop_parsing/parsing.py
   ```

---

### 📂 Additional Description: Upstage API Usage & Preprocessing
1. `Database/diseaseinfo` contains:
   - PDFs converted from captured images from the National Health Information Portal
   - Cropped PDFs for each disease group
2. `api/doc_parse/doc_parsing.py`:
   - Uses the cropped PDFs in `Database/diseaseinfo`
   - Applies Upstage's **Document Parsing API**
   - Saves extracted JSON files to `Database/input`
3. `api/crop_parsing`:
   - Preprocesses parsed JSON files
   - Saves the results in `Database/output/processed_final`

---

### 🐍 Virtual Environment (Optional)
```bash
python3 -m venv agi_ybgirls
source agi_ybgirls/bin/activate
pip install -r requirements.txt
deactivate
```

---

### 🕷️ Crawling Medical Documents
- *(Update dependency list if needed)*:  
  ```bash
  pip freeze > requirements.txt
  ```

- To run the crawler:
  ```bash
  pip install -r requirements.txt
  python Crawling/diseaseinfo_crop.py
  ```

---

### 🧠 Embedding Processed Data & Saving to CSV
```bash
python fin/main.py
```

---

### 📝 Summarization using LangChain
0. Install requirements:  
   ```bash
   pip install -r requirements.txt
   ```
1. Summarization logic implemented in:  
   - `fin/summarization.py`
2. Modularized version in:  
   - `fin/main2.py`

---

### 🚀 Launching the Final Streamlit App
0. Install requirements:  
   ```bash
   pip install -r requirements.txt
   ```
1. Run the app:  
   ```bash
   python -m streamlit run fin/app.py
   ```
