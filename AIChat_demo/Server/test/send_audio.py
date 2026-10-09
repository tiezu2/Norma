import asyncio, websockets, json, struct
from pyogg import OpusEncoder

SAMPLE_RATE = 16000
FRAME_MS = 40
FRAME_SIZE = SAMPLE_RATE // 1000 * FRAME_MS
PROTOCOL_VERSION = 2
TYPE_AUDIO = 0

def pack(version, type_, payload):
    return struct.pack("!HHI", version, type_, len(payload)) + payload

async def main():
    headers = {
        "Authorization": "Bearer 123456",
        "Device-Id": "00:11:22:33:44:55",
        "Protocol-Version": "2",
    }
    async with websockets.connect("ws://127.0.0.1:8000",
                                  extra_headers=headers) as ws:
        await ws.send(json.dumps({
            "type": "hello",
            "audio_params": {"format": "opus", "sample_rate": 16000,
                             "channels": 1, "frame_duration": 40}
        }))
        print("握手:", await ws.recv())

        pcm_path = "../Client/third_party/snowboy/resources/echo.pcm"
        with open(pcm_path, "rb") as f:
            pcm = f.read()

        enc = OpusEncoder()
        enc.set_sampling_frequency(SAMPLE_RATE)
        enc.set_channels(1)
        enc.set_application('voip')

        bytes_per_frame = FRAME_SIZE * 2
        for i in range(0, len(pcm), bytes_per_frame):
            frame = pcm[i:i + bytes_per_frame]
            if len(frame) < bytes_per_frame:
                break
            opus = enc.encode(frame)
            await ws.send(pack(PROTOCOL_VERSION, TYPE_AUDIO, opus))
            await asyncio.sleep(0.04)

        print("音频发送完毕，等待服务端响应...")
        while True:
            try:
                reply = await asyncio.wait_for(ws.recv(), timeout=15)
                print("服务端:", reply)
            except asyncio.TimeoutError:
                break

asyncio.run(main())
