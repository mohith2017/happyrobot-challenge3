# Use an official Python runtime as a parent image
FROM python:3.8-slim

WORKDIR /challenge3
COPY . /challenge3
RUN apt-get update
RUN apt-get install libasound-dev libsndfile1 libportaudio2 libportaudiocpp0 portaudio19-dev -y
RUN apt-get install gcc -y
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE  80
ENV NAME HelloRobots
CMD ["python3", "vad_on_cpu.py"]
