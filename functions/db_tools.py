# functions/db_tools.py
from google.adk.tools.function_tool import FunctionTool
from typing import Optional
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read environment variables (matching docker-compose.yml)
DB_USER = os.getenv("DB_USER", "hospital_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hospital_pass")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "hospital_data")

# Create MySQL connection string
MYSQL_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔌 Trying to connect to: mysql+mysqlconnector://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Try connecting to MySQL
try:
    db = SQLDatabase.from_uri(MYSQL_URI)
    test = db.run("SELECT 1;")
    print("✅ Connected to MySQL successfully!")
    print("Test query result:", test)
except Exception as e:
    print("❌ Connection failed:", e)
    raise e


# 🧩 Tool 1: Get schema
def get_schema(input: Optional[dict] = None) -> dict:
    try:
        if not input or not input.get("table"):
            schema = db.get_table_info()
            print("📘 Full database schema retrieved")
            return {"schema_description": schema}

        table_name = input.get("table")
        schema = db.get_table_info([table_name])
        print(f"📘 Schema retrieved for table: {table_name}")

        lines = [
            line.strip()
            for line in schema.splitlines()
            if line.strip().startswith(tuple("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
            and "PRIMARY KEY" not in line
            and "CREATE TABLE" not in line
            and not line.strip().startswith("/*")
        ]
        clean_schema = "\n".join(lines)

        print("\n📄 Columns:\n", clean_schema)
        return {"schema_description": clean_schema}

    except Exception as ex:
        print("❌ Error getting schema:", ex)
        return {"error": str(ex)}


# 🧩 Tool 2: Run SQL query
def run_sql_query(input: Optional[dict] = None) -> dict:
    sql_query = input.get("query") if input else None
    print("▶️ Running SQL query:", sql_query)

    try:
        result = db.run(sql_query)
        print("✅ Query executed successfully!")
        print("Result:", result)
        return {"raw_result": result}
    except Exception as ex:
        print("❌ SQL execution error:", ex)
        return {"error": str(ex)}


# Create tool instances
get_schema_tool = FunctionTool(get_schema)
run_sql_query_tool = FunctionTool(run_sql_query)