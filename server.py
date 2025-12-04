import os
import json
import asyncio
import websockets

# Maps device_id -> websocket
connected_devices = {}

async def handler(ws, path):
    try:
        async for message in ws:
            data = json.loads(message)

            # 1️⃣ Register the device
            if data.get("type") == "register":
                device_id = data.get("id")
                connected_devices[device_id] = ws
                await ws.send(json.dumps({"status": "registered", "id": device_id}))
                print(f"✅ Registered {device_id}")
                continue

            # 2️⃣ Send message to target device
            if data.get("type") == "send":
                target_id = data.get("to")
                if target_id in connected_devices:
                    await connected_devices[target_id].send(json.dumps({
                        "from": data.get("from"),
                        "message": data.get("message")
                    }))
                    print(f"📤 {data.get('from')} → {target_id}: {data.get('message')}")
                else:
                    await ws.send(json.dumps({"error": True, "reason": "target not connected"}))
    except:
        pass

    # Cleanup disconnected device
    for d_id, sock in list(connected_devices.items()):
        if sock == ws:
            del connected_devices[d_id]
            print(f"❌ Disconnected {d_id}")

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 WebSocket relay running on port {port}")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
