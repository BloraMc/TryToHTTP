import asyncio
import websockets
import socket
# Basic stripped down version

# Configuration
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 25565
WS_URL = "wss://apicol.trytochill.net"
BUFFER_SIZE = 2048

async def pipe(reader, writer, ws_send_func=None, ws_recv_iterator=None):
    """Efficiently moves data between TCP and WebSocket."""
    try:
        if ws_send_func:
            while True:
                data = await reader.read(BUFFER_SIZE)
                if not data: break
                await ws_send_func(data)
        elif ws_recv_iterator:
            async for message in ws_recv_iterator:
                writer.write(message)
                await writer.drain()
    except:
        pass
    finally:
        if not writer.is_closing():
            writer.close()

async def handle_client(reader, writer):
    sock = writer.get_extra_info('socket')
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    
    print(f"Connection received. Connecting to TryToShield @ {WS_URL}")
    
    try:
        async with websockets.connect(WS_URL, family=socket.AF_INET, compression=None) as ws:
            await asyncio.gather(
                pipe(reader, writer, ws_send_func=ws.send),
                pipe(reader, writer, ws_recv_iterator=ws)
            )
    except Exception as e:
        print(f"TryToShield Error: {e}")
    finally:
        writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client, LISTEN_HOST, LISTEN_PORT, family=socket.AF_INET
    )
    for s in server.sockets:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    print(f"Launch Minecraft (any version) and connect to : {LISTEN_HOST}:{LISTEN_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())