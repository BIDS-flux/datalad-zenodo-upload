FROM cicirello/pyaction-lite:3

RUN pip install -r requirements.txt
COPY entrypoint.py /entrypoint.py
ENTRYPOINT ["/entrypoint.py"]
