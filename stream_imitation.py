# #!pip install -q torchaudio
# # !pip install -q onnxruntime
import numpy as np
import websockets
import asyncio

SAMPLING_RATE = 16000

import torch
torch.set_num_threads(1)

from IPython.display import Audio
from pprint import pprint

async def test():
    # download example
    torch.hub.download_url_to_file('https://models.silero.ai/vad_models/en.wav', 'en_example.wav')

    USE_ONNX = True # change this to True if you want to test onnx model
    
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                model='silero_vad',
                                force_reload=True,
                                onnx=USE_ONNX)

    (get_speech_timestamps,
    save_audio,
    read_audio,
    VADIterator,
    collect_chunks) = utils

    wav = read_audio('en_example.wav', sampling_rate=SAMPLING_RATE)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=SAMPLING_RATE)
    pprint(speech_timestamps)

    # merge all speech chunks to one audio
    save_audio('only_speech.wav',
            collect_chunks(speech_timestamps, wav), sampling_rate=SAMPLING_RATE) 
    Audio('only_speech.wav')

    ## using VADIterator class
    vad_iterator = VADIterator(model)
    wav = read_audio(f'en_example.wav', sampling_rate=SAMPLING_RATE)
    # print("Wav: ", wav)
    # print("Type of wav: ", type(wav))

    window_size_samples = 1536 # number of samples in a single audio chunk
    for i in range(0, len(wav), window_size_samples):
        chunk = wav[i: i+ window_size_samples]
        audio_chunk = bytearray(chunk.numpy())

        async with websockets.connect('wss://localhost:8000/api/v1/listen') as websocket:
            await websocket.send(audio_chunk)
            response = await websocket.recv()
            print(response)
        
        if len(chunk) < window_size_samples:
            break
        speech_dict = vad_iterator(chunk, return_seconds=True)
        if speech_dict:
            print(speech_dict, end=' ')
            print(type(speech_dict))
    vad_iterator.reset_states() # reset model states after each audio

asyncio.get_event_loop().run_until_complete(test())

