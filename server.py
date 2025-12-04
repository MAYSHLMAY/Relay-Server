import os
import asyncio
import websockets
import json

PORT = int(os.getenv("PORT", 8080))

connected_clients = {}  # device_id -> websocket

async def handler(ws, path):
    device_id = None
    print("Client connected")
    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            # Register device
            if data.get("type") == "register" and "id" in data:
                device_id = data["id"]
                connected_clients[device_id] = ws
                print(f"✅ Registered device {device_id}")
                continue

            # Forward messages to target device
            target_id = data.get("to")
            if target_id and target_id in connected_clients:
                target_ws = connected_clients[target_id]
                try:
                    await target_ws.send(json.dumps(data))
                    print(f"📤 Forwarded message from {device_id} → {target_id}")
                except:
                    print(f"❌ Failed to send to {target_id}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {device_id} disconnected")
    finally:
        if device_id in connected_clients:
            del connected_clients[device_id]

async def main():
    print(f"🌐 WebSocket relay running on port {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()  # keep running

asyncio.run(main())
