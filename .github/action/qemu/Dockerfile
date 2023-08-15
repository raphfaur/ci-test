FROM balenalib/qemux86-64-debian-python:latest

COPY qemu.py /qemu.py
COPY boot.img /boot.img

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "/qemu.py" ]
