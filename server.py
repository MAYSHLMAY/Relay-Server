import os
import asyncio
import websockets

PORT = int(os.getenv("PORT", 8080))

async def handler(ws, path):
    print("Client connected")
    try:
        async for msg in ws:
            print("Received:", msg)
            await ws.send("Echo: " + msg)
    except:
        print("Client disconnected")

async def main():
    print(f"🌐 WebSocket relay running on port {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

asyncio.run(main())
