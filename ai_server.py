import socket
import threading
from openai import OpenAI

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 5000
MODEL = "gpt-4o-mini"
MAX_TOKENS = 600   # Increase for longer replies (safe: 300–800)

# =========================================

client_ai = OpenAI()
clients = []

# ---------- OpenAI request ----------
def ask_openai(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an ESP32 device."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[AI ERROR] {e}"

# ---------- Reliable long message sender ----------
def send_long_message(client, message):
    data = message.encode("utf-8")
    length = len(data)

    # Send length header
    client.sendall(f"{length}\n".encode("utf-8"))

    # Send full payload
    client.sendall(data)

# ---------- Client handler ----------
def handle_client(client, addr):
    print(f"[CONNECTED] {addr}")
    clients.append(client)

    try:
        buffer = b""

        while True:
            chunk = client.recv(1024)
            if not chunk:
                break

            buffer += chunk

            # Process full lines from ESP32
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                msg = line.decode().strip()

                if not msg:
                    continue

                print(f"[ESP32] {msg}")

                # Send to OpenAI
                ai_reply = ask_openai(msg)
                print(f"[AI] {ai_reply[:120]}...")

                # Send full AI response back to same ESP32
                send_long_message(client, ai_reply)

    except Exception as e:
        print(f"[ERROR] {addr} -> {e}")

    print(f"[DISCONNECTED] {addr}")
    clients.remove(client)
    client.close()

# ---------- Server ----------
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("===================================")
    print(" ESP32 ↔ OpenAI AI Chat Server")
    print(f" Listening on port {PORT}")
    print("===================================")

    while True:
        client, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(client, addr),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()
