FROM debian:latest

COPY qemu.py /qemu.py
COPY boot.img /boot.img
COPY requirements.txt /requirements.txt

RUN "apt update && apt -y install && apt install qemu-system-x86 &&  pip install --no-cache-dir -r /requirements.txt"

ENTRYPOINT [ "python", "/qemu.py" ]
