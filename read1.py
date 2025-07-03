#!/usr/bin/env python3
import requests
import sys

API_URL = "http://127.0.0.1:5002/api/query"

def send_query(question):
    try:
        response = requests.post(API_URL, json={"query": question}, timeout=30)
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def display_result(data):
    if "error" in data:
        print(f"❌ Error: {data['error']}")
    else:
        print("\n🔍 SQL Query:")
        print(data.get("sql", "[No SQL generated]"))
        print("\n📊 Result:")
        result = data.get("result", [])
        if isinstance(result, list):
            if result:
                headers = result[0].keys()
                print(" | ".join(headers))
                print("-" * 40)
                for row in result:
                    print(" | ".join(str(row.get(h, '')) for h in headers))
            else:
                print("No records found.")
        else:
            print(result)

def main():
    print("🩺 Ask your hospital database question (type 'exit' to quit)")
    while True:
        question = input("❓> ").strip()
        if question.lower() in ['exit', 'quit']:
            print("👋 Exiting.")
            break
        if not question:
            continue
        response = send_query(question)
        display_result(response)

if __name__ == "__main__":
    main()
