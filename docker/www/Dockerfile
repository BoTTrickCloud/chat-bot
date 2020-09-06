FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY ./docker/www/chat.conf /etc/nginx/conf.d
COPY ./www /usr/share/nginx/html/

RUN chmod -R ug=rwX,o=rX /usr/share/nginx/html/
