FROM nginx:alpine
RUN apk add certbot certbot-nginx
RUN pip3 install flask flask_jwt_extended
RUN crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -

COPY ./src/ /npmlite
COPY ./data/ /npmlite/initial_data

RUN mkdir /data
RUN mv /npmlite/initial_data/nginx_conf/nginx.conf /etc/nginx
RUN mv /npmlite/initial_data/nginx_conf/default.conf /etc/nginx/conf.d
RUN mv /npmlite/initial_data/nginx_conf/*.html /usr/share/nginx/html

EXPOSE 80 443
WORKDIR /npmlite
CMD nginx && python3 app.py

LABEL org.label-schema.schema-version="1.0.0" \
    org.label-schema.license="MIT" \
    org.label-schema.name="nginx-proxy-manager-lite" \
    org.label-schema.description="Lightweight Docker container for managing Nginx hosts with REST api and a simple, minimal web UI" \
    org.label-schema.url="https://github.com/Sajjal/Nginx-Proxy-Manager-Lite" \
    org.label-schema.vcs-url="https://github.com/Sajjal/Nginx-Proxy-Manager-Lite.git" \
    org.label-schema.cmd="docker run --it mrsajjal/npmlite:latest"