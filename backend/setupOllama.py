import httpx

def test_ollama():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3:mini",   # change if you want another model
        "prompt": "Hello Ollama, respond in one short line.",
        "stream": False
    }

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, json=payload)
            print(f"Status code: {resp.status_code}")
            print("Raw response:", resp.text)

            if resp.status_code == 200:
                data = resp.json()
                print("\n✅ Ollama response:")
                print(data.get("response", "No 'response' key in result"))
            else:
                print("\n⚠️ Ollama did not return 200 OK")
    except Exception as e:
        print(f"❌ Error contacting Ollama: {e}")

if __name__ == "__main__":
    test_ollama()
