from google.adk.tools.function_tool import FunctionTool
import ast
from typing import Optional
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create MySQL connection string
MYSQL_URI = (
    f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
)

print(f"🔌 Trying to connect to: {MYSQL_URI}")

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
# def get_schema(input: Optional[dict] = None) -> dict:
#     try:
#         if isinstance(input, dict):
#             table_name = input.get("table")
#             schema = db.get_table_info([table_name])
#             print(f"📘 Schema retrieved for table: {table_name}")

#             # ✅ Extract only column definitions
#             lines = [
#                 line.strip()
#                 for line in schema.splitlines()
#                 if line.strip().startswith(tuple("\tabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
#                 and "PRIMARY KEY" not in line
#                 and "CREATE TABLE" not in line
#                 and not line.strip().startswith("/*")
#             ]
#             clean_schema = "\n".join(lines)

#             print("\n📄 Columns:\n", clean_schema)
#             return {"schema_description": clean_schema}

#         elif input is None:
#             schema = db.get_table_info()
#             print("📘 Full database schema retrieved")
#             return {"schema_description": schema}
#         else:
#             print("⚠️ Invalid input format for get_schema()")
#             return {"error": "Invalid input format. Expected dict or None."}

#     except Exception as ex:
#         print("❌ Error getting schema:", ex)
#         return {"error": str(ex)}
def get_schema(input: Optional[dict] = None) -> dict:
    try:
        # If input is None or doesn't contain a valid table name → get full schema
        if not input or not input.get("table"):
            schema = db.get_table_info()
            print("📘 Full database schema retrieved")
            return {"schema_description": schema}

        table_name = input.get("table")
        schema = db.get_table_info([table_name])
        print(f"📘 Schema retrieved for table: {table_name}")

        # Clean the CREATE TABLE definition
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
get_schema_tool = FunctionTool(get_schema)
run_sql_query_tool = FunctionTool(run_sql_query)

# # 🧠 Main interactive section
# if __name__ == "__main__":
#     print("\n=== MySQL DB Tools ===")
#     print("1️⃣  View Schema")
#     print("2️⃣  Run SQL Query")
#     choice = input("Enter your choice (1 or 2): ").strip()

#     if choice == "1":
#         table = input("Enter table name (or leave empty for all): ").strip()
#         if table:
#             output = get_schema({"table": table})
#         else:
#             output = get_schema()
#         print("\n🧾 Output:\n", output["schema_description"])

#     elif choice == "2":
#         query = input("Enter SQL query: ").strip()
#         output = run_sql_query({"query": query})
#         print("\n🧾 Output:\n", output)

#     else:
#         print("⚠️ Invalid choice. Please enter 1 or 2.")
