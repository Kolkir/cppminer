# Configure Docker environment for code2seq project
``
cd docker
docker build -t code2seq:1.0 .
docker run -it -v [host_dataset_path]:[container_dataset_path] code2seq:1.0 bash
cd /code2seq
``

