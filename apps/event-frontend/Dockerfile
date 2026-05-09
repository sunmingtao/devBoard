FROM node:22-alpine AS build-stage

WORKDIR /app

ARG VITE_BASE_PATH=/events/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}

COPY package*.json ./
RUN npm install --include=dev --no-audit --no-fund

COPY . .
RUN npm run build

FROM nginx:alpine AS production-stage

RUN apk upgrade --no-cache

RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY --from=build-stage --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    sed -i '/^user /d' /etc/nginx/nginx.conf && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

EXPOSE 8080

USER nginx

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/events/ || exit 1

ENTRYPOINT ["nginx", "-g", "daemon off;"]
