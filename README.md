# To run the files:
- Run python vad_on_cpu.py for server to be listening
- Test the websocket listening at http://localhost:3000/api/v1/listen

# To replicate from docker
- Docker pull https://hub.docker.com/repository/docker/mohith2017/vad/general
- docker run -it 3000:8000 mohith2017/vad
- Test the websocket listening at http://localhost:3000/api/v1/listen
