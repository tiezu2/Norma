import asyncio
import websockets
import json
import queue
from handle.text_handler import TextHandler
from handle.audio_handler import AudioHandler
from handle.auth_handler import AuthHandler
from service_manager import ServiceManager

import sys
sys.path.append("..")
from tools.logger import logger

class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=8000, access_token="123456", device_id="00:11:22:33:44:55", protocol_version=2, service_manager: ServiceManager = None):
        self.host = host
        self.port = port
        self.service_manager = service_manager
        self.text_handler = TextHandler(self.service_manager)
        self.audio_handler = AudioHandler(self.service_manager)
        self.auth_handler = AuthHandler(access_token, device_id, protocol_version)

    async def process_send_queue(self, websocket):
        while True:
            try:
                if not self.service_manager.ws_send_queue.empty():
                    data = self.service_manager.ws_send_queue.get_nowait()
                    await websocket.send(data)
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"发送队列处理错误: {e}")

    async def handle_client(self, websocket, path):
        logger.info("Client connected")
        process_task = None
        try:
            process_task = asyncio.create_task(self.process_send_queue(websocket))
            headers = websocket.request_headers
            if not self.auth_handler.authenticate(headers):
                await websocket.send(json.dumps({"type": "auth", "message": "Authentication failed"}))
                await websocket.close(reason="Authentication failed")
                logger.error("Authentication failed for client")
                return
            response = {
                "type": "auth",
                "message": "Client authenticated",
            }
            await websocket.send(json.dumps(response))
            async for message in websocket:
                if isinstance(message, bytes):
                    await self.audio_handler.handle_audio_message(message)
                else:
                    text = json.loads(message)
                    await self.text_handler.handle_text_message(text)
        except websockets.exceptions.ConnectionClosed as e:
            if process_task:
                process_task.cancel()
            logger.warning(f"Connection closed: {e}")
            self.service_manager.reset_services()
        finally:
            if process_task:
                process_task.cancel()
            logger.info("Client disconnected")
            self.service_manager.reset_services()

    async def start_server(self):
        async def process_request(path, request_headers):
            logger.info(f"[REQ] PATH={path}")
            logger.info(f"[REQ] HEADERS={dict(request_headers)}")
            return None

        async with websockets.serve(
            self.handle_client, self.host, self.port,
            process_request=process_request,
        ):
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            await asyncio.Future()
