FROM python:2.7

WORKDIR /usr/src/app

COPY . .

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai

RUN pip install --no-cache-dir -r requirements.txt && \
	echo "# ! /bin/sh " > /usr/src/app/run.sh && \
	echo "cd Run" >> /usr/src/app/run.sh && \
	echo "python main.py" >> /usr/src/app/run.sh && \
	chmod 777 run.sh

EXPOSE 5000

CMD [ "sh", "run.sh" ]