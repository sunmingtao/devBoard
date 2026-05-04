FROM node:22-alpine AS build-stage

WORKDIR /app

ARG VITE_BASE_PATH=/events/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}

COPY package*.json ./
RUN npm install --include=dev --no-audit --no-fund

COPY . .
RUN npm run build

FROM nginx:alpine AS production-stage

RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:80/events/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
