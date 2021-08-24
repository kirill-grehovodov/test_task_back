FROM python:3.6

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN chmod a+x ./run.sh

ENTRYPOINT ["./tun.sh"]


#CMD python ./backend/manage.py runserver

# ENTRYPOINT ["python", "test.py"]