FROM python:3
COPY ./requirements.txt /requirements.txt
WORKDIR /
RUN pip3 install -r requirements.txt
COPY ./Eye_of_STAROSTA /Eye_of_STAROSTA
COPY ./database /database
<<<<<<< HEAD
=======
COPY ./config.cfg /config.cfg
COPY ./opt /opt
>>>>>>> 7ab8d015da9efcb880252edf1403094d8c16462d
ENTRYPOINT [ "python3" ]
CMD [ "./Eye_of_STAROSTA/eye_of_STAROSTA.py" ]
