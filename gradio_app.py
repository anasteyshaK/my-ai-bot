
import gradio as gr
import requests
import traceback

API_URL = "http://localhost:8080/at_data/answer"


def ask_bot(message, history):
    all_messages = []

    print("\n" + "=" * 60)
    print("NEW REQUEST")
    print("=" * 60)

    try:
        print(f"User message: {message}")
        print(f"History: {history}")

        for item in history:
            if isinstance(item, dict):
                role = item.get("role")
                content = item.get("content")

                if role in ("user", "assistant") and isinstance(content, str):
                    if content.strip():
                        all_messages.append(content)

            elif isinstance(item, (list, tuple)) and len(item) == 2:
                user_msg, bot_msg = item

                if isinstance(user_msg, str) and user_msg.strip():
                    all_messages.append(user_msg)

                if isinstance(bot_msg, str) and bot_msg.strip():
                    all_messages.append(bot_msg)

        if not isinstance(message, str) or not message.strip():
            return "Error: Message cannot be empty."

        all_messages.append(message.strip())

        print("\nMessages sent to API:")
        for i, msg in enumerate(all_messages):
            print(f"{i + 1}. {msg[:300]}")

        print(f"\nAPI URL: {API_URL}")
        print("Sending request...")

        response = requests.post(
            API_URL,
            json=all_messages,
            timeout=180
        )

        print(f"\nHTTP status: {response.status_code}")
        print(f"Response body: {response.text[:3000]}")

        response.raise_for_status()

        data = response.json()

        if "answer" not in data:
            print("ERROR: Missing 'answer' field")
            return f"Invalid API response: {data}"

        answer = data["answer"]

        print("\nSUCCESS")
        print(f"Answer: {answer[:1000]}")
        print("=" * 60 + "\n")

        return answer

    except requests.exceptions.Timeout:
        print("\nERROR: Request timeout")
        traceback.print_exc()
        return "Connection error: The AI server took too long to respond."

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to FastAPI")
        traceback.print_exc()
        return "Connection error: FastAPI is unavailable at localhost:8080."

    except requests.exceptions.HTTPError as e:
        print("\nHTTP ERROR")
        traceback.print_exc()

        try:
            detail = e.response.json().get("detail", str(e))
        except (ValueError, AttributeError):
            detail = str(e)

        return f"API error {e.response.status_code}: {detail}"

    except requests.exceptions.RequestException as e:
        print("\nREQUEST ERROR")
        traceback.print_exc()
        return f"Connection error: {e}"

    except Exception as e:
        print("\nUNEXPECTED ERROR")
        traceback.print_exc()
        return f"Unexpected error: {type(e).__name__}: {e}"

demo = gr.ChatInterface(
    fn=ask_bot,
    title="Allied Testing AI Assistant",
    description="Ask questions about Allied Testing services and company information."
)


if __name__ == "__main__":
    print("=" * 60)
    print("STARTING ALLIED TESTING AI ASSISTANT")
    print(f"API endpoint: {API_URL}")
    print("Gradio URL: http://0.0.0.0:7860")
    print("=" * 60)

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
