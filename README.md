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
