FROM python:3

WORKDIR /app

COPY . .

RUN pip install urllib3 --upgrade
RUN pip install -r requirements.txt

CMD taskiq scheduler broker:scheduler & taskiq worker broker:broker & python schedule.py & python main.py
