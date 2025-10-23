FROM cicirello/pyaction-lite:3

RUN apk add --no-cache py3-pip git git-annex

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY entrypoint.py /entrypoint.py
ENTRYPOINT ["/entrypoint.py"]
