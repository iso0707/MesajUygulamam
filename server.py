import os
import json
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


app = FastAPI()

clients = {}


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Mesaj sunucusu çalışıyor!"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    username = None

    try:

        # İlk mesaj kullanıcı adı olacak
        username_data = await websocket.receive_text()

        try:
            data = json.loads(username_data)
            username = data.get("type") == "login" and data.get("username")
        except Exception:
            username = None

        if not username:
            username = "Kullanıcı"

        clients[websocket] = username

        print(f"{username} bağlandı.")

        # Bağlanan kişiye hoş geldin
        await websocket.send_text(json.dumps({
            "type": "system",
            "message": f"Hoş geldin, {username}!"
        }, ensure_ascii=False))

        # Diğer kullanıcılara katıldı mesajı
        for client in list(clients):

            if client != websocket:

                try:
                    await client.send_text(json.dumps({
                        "type": "system",
                        "message": f"{username} sohbete katıldı."
                    }, ensure_ascii=False))

                except Exception:
                    pass

        while True:

            raw_message = await websocket.receive_text()

            try:
                data = json.loads(raw_message)
            except Exception:
                data = {
                    "type": "message",
                    "message": raw_message
                }

            if data.get("type") != "message":
                continue

            message = str(data.get("message", "")).strip()

            if not message:
                continue

            now = datetime.now().strftime("%H:%M")

            message_data = {
                "type": "message",
                "username": username,
                "message": message,
                "time": now
            }

            print(f"[{now}] {username}: {message}")

            # Herkese gönder
            for client in list(clients):

                if client != websocket:

                    try:

                        await client.send_text(
                            json.dumps(
                                message_data,
                                ensure_ascii=False
                            )
                        )

                    except Exception:
                        pass

    except WebSocketDisconnect:

        if websocket in clients:

            old_username = clients.pop(websocket)

            print(f"{old_username} ayrıldı.")

            # Diğerlerine haber ver
            for client in list(clients):

                try:

                    await client.send_text(json.dumps({
                        "type": "system",
                        "message": f"{old_username} sohbetten ayrıldı."
                    }, ensure_ascii=False))

                except Exception:
                    pass

    except Exception as error:

        print("Sunucu hatası:", error)

        if websocket in clients:
            clients.pop(websocket, None)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))

    print("===================================")
    print("       MESAJ UYGULAMASI")
    print("===================================")
    print(f"Port: {port}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
