FROM python:3.10-slim


COPY *.py /cloud_run_service/
COPY requirements.txt /cloud_run_service/

WORKDIR /cloud_run_service

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 444 app.py
RUN chmod 444 requirements.txt

EXPOSE 8080

CMD [ "python", "app.py" ]
