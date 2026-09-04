import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


app = FastAPI()

clients = []


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Mesaj sunucusu çalışıyor!"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    clients.append(websocket)

    print("Yeni cihaz bağlandı.")

    try:

        while True:

            message = await websocket.receive_text()

            print("Mesaj:", message)

            for client in clients:

                if client != websocket:

                    try:
                        await client.send_text(message)
                    except Exception:
                        pass

    except WebSocketDisconnect:

        if websocket in clients:
            clients.remove(websocket)

        print("Bir cihaz ayrıldı.")

    except Exception:

        if websocket in clients:
            clients.remove(websocket)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))

    print("===================================")
    print("     MESAJ UYGULAMASI SUNUCUSU")
    print("===================================")
    print(f"Port: {port}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
