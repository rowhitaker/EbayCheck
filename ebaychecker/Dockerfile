from jazzdd/alpine-flask
MAINTAINER Ricky Whitaker

EXPOSE 5000

# application folder
ENV APP_DIR /ebaychecker

# app dir
RUN mkdir ${APP_DIR} \
	&& chown -R nginx:nginx ${APP_DIR} \
	&& chmod 777 /run/ -R \
	&& chmod 777 /root/ -R
VOLUME [${APP_DIR}]
WORKDIR ${APP_DIR}

COPY entrypoint.sh /ebaychecker/entrypoint.sh
RUN chmod 777 /ebaychecker/entrypoint.sh

RUN pip install requests

ENTRYPOINT ["/ebaychecker/entrypoint.sh"]
