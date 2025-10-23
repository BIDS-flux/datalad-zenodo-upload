FROM cicirello/pyaction-lite:3

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY entrypoint.py /entrypoint.py
ENTRYPOINT ["/entrypoint.py"]
