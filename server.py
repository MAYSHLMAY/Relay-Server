import asyncio
import websockets

PORT = 8080
connected = {}  # device_id -> websocket

async def handler(ws, path):
    device_id = None
    try:
        async for msg in ws:
            if isinstance(msg, str):
                data = msg.split(" ", 1)
                if data[0] == "REGISTER":
                    device_id = data[1]
                    connected[device_id] = ws
                    print(f"✅ Registered device {device_id}")
                elif data[0] == "FORWARD":
                    # FORWARD target_id rest_of_msg
                    target_id, payload = data[1].split(" ", 1)
                    if target_id in connected:
                        await connected[target_id].send(payload)
            else:
                # binary data forwarding
                # expect the first 36 bytes to be header: TARGET_ID|SEQ|TOTAL
                header_len = 36
                header = msg[:header_len].decode()
                target_id, seq, total = header.split("|")
                if target_id in connected:
                    await connected[target_id].send(msg)
    except websockets.ConnectionClosed:
        if device_id in connected:
            del connected[device_id]
        print(f"❌ Disconnected {device_id}")

async def main():
    print(f"🌐 WebSocket relay running on port {PORT}")
    async with websockets.serve(
        handler, "0.0.0.0", PORT,
        ping_interval=30, ping_timeout=60, max_size=None
    ):
        await asyncio.Future()

asyncio.run(main())
