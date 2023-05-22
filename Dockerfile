FROM python:alpine
COPY . /vktotg
WORKDIR /vktotg
RUN pip3 install -r requirements.txt
CMD ["python3", "bot.py"]