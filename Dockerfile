FROM python:3.11-slim-buster

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY api.py api.py
COPY data.py data.py
COPY postgres.py postgres.py
COPY SummaryRecipe.py SummaryRecipe.py

CMD [ "python3", "-m" , "api"]