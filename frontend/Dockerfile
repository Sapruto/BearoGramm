FROM node:20-alpine AS build
WORKDIR /app

RUN corepack enable

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

ARG VITE_API_URL=/api
ARG VITE_WS_URL=/ws
ENV VITE_API_URL=$VITE_API_URL \
    VITE_WS_URL=$VITE_WS_URL

RUN yarn build

FROM alpine:3.20
WORKDIR /app
COPY --from=build /app/dist ./dist
CMD ["true"]