FROM python:2.7

WORKDIR /app

COPY . .

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai
ENV ENTRY=main

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5010
CMD python Run/${ENTRY}.py