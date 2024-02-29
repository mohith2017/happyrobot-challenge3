import torch
import numpy as np
# import pyaudio
import audioop
import websockets
import asyncio
import json

vad_model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad",
    onnx=True,
)
get_speech_ts, _, _, VADIterator, _ = utils

VAD_SAMPLING_RATE = 8000
VAD_WINDOW_SIZE_EXAMPLES = 512

vad_iterator = VADIterator(vad_model, threshold=0.7, sampling_rate=VAD_SAMPLING_RATE)
accum_buffer = np.array([])
duration = 0
activities = {} 

SAMPLE_RATE = 16000

 
# create handler for each connection
async def handler(websocket, path):

    # Set the path, get the audio chunks and process the chunks
    if path == "/api/v1/listen":
        audio_chunk = await websocket.recv()
        # print(audio_chunk)
        chunk = np.frombuffer(audio_chunk, np.int16)
        
        reply = f"Data received as:  {chunk}!"
        print(reply)

        sample_rate = SAMPLE_RATE

        # Resample to VAD input sampling rate
        if sample_rate != VAD_SAMPLING_RATE:
            chunk, _ = audioop.ratecv(
                chunk, 2, 1, sample_rate, VAD_SAMPLING_RATE, None
            )
        
        accum_buffer = np.concatenate((accum_buffer, chunk))
        # Process the buffer
        processed_windows_count = 0
        for i in range(0, len(accum_buffer), VAD_WINDOW_SIZE_EXAMPLES):
            if i + VAD_WINDOW_SIZE_EXAMPLES > len(accum_buffer):
                break

            processed_windows_count += 1
            speech_dict = vad_iterator(accum_buffer[i: i + VAD_WINDOW_SIZE_EXAMPLES], return_seconds=True)

            if speech_dict:
                if "start" in speech_dict:
                    activities["start"] = speech_dict["start"]
                else:
                    activities["end"] = speech_dict["end"]

        # Remove processed audio from buffer
        accum_buffer = accum_buffer[processed_windows_count * VAD_WINDOW_SIZE_EXAMPLES:]
        
        # Send activities to websocket
        await websocket.send(json.dumps({"activity": activities, "accum_duration": duration}))
 

# Allow servers from any IP address to connect
start_server = websockets.serve(handler, "0.0.0.0", 8000) 
 
 
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
