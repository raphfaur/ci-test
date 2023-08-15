FROM debian:latest

COPY qemu.py /qemu.py
COPY boot.img /boot.img
COPY requirements.txt /requirements.txt

RUN apt update && apt -y install && apt install -y qemu-system-x86 

ENTRYPOINT [ "python", "/qemu.py" ]
