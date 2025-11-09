# Hospital Resource Management System 🏥

AI-powered hospital resource management system for Pune with real-time monitoring and analytics.

## 🚀 Quick Setup Guide

### 1️⃣ Clone & Install Dependencies
```bash
git clone https://github.com/manyaababbar/froncort.git
cd froncort
pip install -r requirements.txt
```

### 2️⃣ Setup Database

**Step 1: Create the database**
```bash
mysql -u root -p
```

**Step 2: Inside MySQL, run:**
```sql
CREATE DATABASE pune_hospitals;
EXIT;
```

**Step 3: Generate and import hospital data**
```bash
python databasehospital.py
mysql -u root -p pune_hospitals < mock_pune_50_hospitals.sql
```

### 3️⃣ Configure Environment Variables

Create a `.env` file in the project root directory:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=pune_hospitals
GOOGLE_API_KEY=your_google_api_key
```

**Note:** Replace `your_password` and `your_google_api_key` with your actual credentials.

### 4️⃣ Start the Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend is now running at: **http://localhost:8000**

📖 API Documentation: **http://localhost:8000/docs**

### 5️⃣ Start the Frontend Server
```bash
cd frontend
npm install
npm run dev
```

✅ Frontend is now running at: **http://localhost:3000**

---

## 📊 What's Included

- ✅ **50 Pune hospitals** with realistic metadata
- ✅ **Real-time tracking** of beds, ICU, and ventilators
- ✅ **Staff management** with doctor and nurse allocation
- ✅ **Resource monitoring** including oxygen supply and medical equipment
- ✅ **Financial analytics** with monthly expenditure and revenue data
- ✅ **AI-powered insights** using Google's Generative AI

---

---

**Need help?** Open an issue on GitHub or contact the maintainers.
