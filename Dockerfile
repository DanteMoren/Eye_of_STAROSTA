FROM python:3
COPY ./requirements.txt /requirements.txt
WORKDIR /
RUN pip3 install -r requirements.txt
COPY ./Eye_of_STAROSTA /Eye_of_STAROSTA
COPY ./database /database
COPY ./config.cfg /config.cfg
ENTRYPOINT [ "python3" ]
CMD [ "./Eye_of_STAROSTA/eye_of_STAROSTA.py" ]
