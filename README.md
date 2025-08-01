# 💰 DeepSeek AI - Personal Financial Advisor & Expense Tracker  

🚀 **DeepSeek AI** helps you track and analyze your **personal finances** by integrating AI-powered **expense tracking, SQL generation, and financial insights**. It’s a **self-hosted** AI-powered bookkeeper that securely manages your financial data **without cloud dependency**.

---

## ✨ Features  

- 📂 **CSV-Based Expense Tracking** – Upload your **bank transactions CSV** to analyze spending.  
- 📊 **AI Categorization** – DeepSeek AI intelligently classifies transactions (e.g., Groceries, Rent, Travel).  
- 🧠 **AI-Powered Insights** – Get **actionable financial advice** based on your transactions.  
- 🏦 **Database Integration** – Store transactions in **PostgreSQL** for historical analysis.  
- 🔍 **AI-Generated SQL Queries** – Just ask **natural language financial questions**, and DeepSeek will generate & execute SQL queries to fetch insights.  
- 🔄 **Auto-Correcting AI Queries** – If SQL fails, AI **retries and refines** the query until it works.  
- 📈 **Financial Visualization** – Get **bar charts, spending trends, and breakdowns** automatically.  
- 🔐 **100% Local & Private** – Runs on **your own machine** with **Ollama & PostgreSQL** (no cloud data sharing).  

---

## 🛠️ Tech Stack  

- **AI Model**: DeepSeek R1 (Running locally via **Ollama**)  
- **UI**: Streamlit  
- **Database**: PostgreSQL  
- **Backend**: Python  

---


## 🔧 Setup Instructions  

### 1️⃣ Install Dependencies  

```bash
pip install -r requirements.txt
```

### 2️⃣ Set Up PostgreSQL Database  

Ensure you have **PostgreSQL running locally** and update your **.env** file with database credentials:

```plaintext
POSTGRES_HOST='your_db_host'
POSTGRES_PORT='5432'
POSTGRES_USER='your_db_user'
POSTGRES_PASSWORD='your_db_password'
POSTGRES_DB='your_db_name'
```

### 3️⃣ Run Ollama Locally  

Make sure **DeepSeek AI** is available via **Ollama**:

```bash
ollama run deepseek-r1:8b
```

### 4️⃣ Start the Streamlit App  

```bash
streamlit run app/main.py
```

---

## 🏗️ How It Works  

1️⃣ **Upload Your Transactions** – Upload a CSV file of your **bank transactions**.  
2️⃣ **AI Categorization & Graphs** – AI **automatically categorizes** transactions and shows insights with **bar charts**.  
3️⃣ **Store in Database** – Click **"Load Data to PostgreSQL"** to store your transactions for historical analysis.  
4️⃣ **Ask AI Financial Questions** – Example:  
   - *"What was my biggest expense last month?"*  
   - *"How much did I spend on groceries this year?"*  
5️⃣ **AI Generates & Executes SQL** – AI **converts the question into SQL, runs it, and provides answers**.  
6️⃣ **Self-Correcting Queries** – If the query **fails**, AI **refines and retries** until it works.  

---

## 🎯 Example Queries  

✅ **"What was my biggest expense last month?"** → AI generates:  

```sql
SELECT MAX(amount), description FROM upload_transactions WHERE transaction_type = 'Expense' AND month_year = '2024-01';
```

✅ **"How much have I spent on food?"** → AI generates:  

```sql
SELECT SUM(amount) FROM upload_transactions WHERE category = 'Food';
```

---

## 🔥 Future Improvements  

- ✅ More AI-powered **financial insights**  
- ✅ Interactive **dashboard with filters**  
- ✅ Support for **multiple banks & currencies**  
- ✅ Export **customized financial reports**  

---

## 💡 Contribute & Feedback  

I built this project to **securely manage my finances using AI** and help others do the same.  
If you find it useful or have suggestions, **feel free to contribute** or **open an issue**!  

📩 **Let’s improve this together!**  

---

💙 **If you found this useful, give it a ⭐ on GitHub and share your thoughts!**  


## Executable File List
Note: If it is a streamlit, update your launch.json accordingly in your own vscode environment. This is important for debugging.
1. login.py (Python) (Streamlit)
- Login/Logout authentication with simple config file as database
- Upload csv file and populate data in md table format and generate graph (specified csv formatted file)
- Perform AI analysis to the csv file uploaded
- (WIP) Add data from uploaded csv file to database
2. sharepoint_connection.py (Python)
- Connect sharepoint to perform file download, file upload, file edit, file reading 
3. medical_scrap_deep.py (Python) (RAG based)
- process user query and lookup to pubmed or arxiv, then generate AI response according to the top x article found
- NOTE: Potentially can be used for future automation
4. rag_deep.py (Python) (Streamlit) (RAG based)
- upload pdf to specific folder, and allow AI to do RAG and lookup into the uploaded document to generated response
5. rag_deep_multi_doc.py (Python) (RAG based)
- similar to rag_deep.py, but support multiple document loading. Take time to process document into VECTOR which is a challenge
6. sciencedirect_web_scrap.py (Python) (Web Scrap)
- WIP due to challenge of sciencedirect which is blocked by paywall, and scrapping is not successfull, potentially due to their security enhancement
7. selenium_test.py (Python) (Web Scrap)
- testing code for selenium on lookup existing element that can be reference from HTML DOM
8. pubmed_web_scrap.py (Python) (Web Scrap)
- successful web scrapping, which is integrated into medical_scrap_deep.py for conditional processing for pubmed
9. rag_deep_remote.py (Python) (RAG Based) (Remote AI/Database Server)

## Youtube study
1. Deepseek explanation 
- https://www.youtube.com/watch?v=4ptWsPi46Nc&t=160s&ab_channel=techie_ray
2. Deepseek Fine Tuning Guide 
- https://www.youtube.com/watch?v=fUT332Y2zA8&ab_channel=MervinPraison
- https://www.youtube.com/watch?v=ZqoZDI0p1aI&t=416s&ab_channel=AIAnytime
- https://www.youtube.com/watch?v=DM-kAwsFf1U&ab_channel=FreeBirdsCrew-DataScienceandGenAI
3. Deepseek RAG Guide
- https://www.youtube.com/watch?v=qNUbPw62-rk&ab_channel=KrishNaik
NOTE: Refer to googlesheet on the difference of RAG and Fine Tuning

## IMPORTANT NOTES
### Sharepoint authentication: Generate self sign cert
Refer to https://www.merge.dev/blog/sharepoint-api-python. In this guide, take note on the section **Authenticate with ClientContext**. Following this step, navigate to https://github.com/vgrem/Office365-REST-Python-Client/wiki/How-to-connect-to-SharePoint-Online-with-certificate-credentials for the commands to generate self sign cert

### Spacy language model installation: Library used to extract keyword from sentence for web scrapping
After installed spacy using command `pip install spacy`, make sure that the language model is also installed using command `python -m spacy download en_core_web_sm`. Make sure this is done **when you are inside your python virtual environment**
