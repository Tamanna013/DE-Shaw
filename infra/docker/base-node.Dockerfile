# Pinned digest for node:20-alpine
FROM node:20-alpine@sha256:d8fb6bf21ca2b0bb8e9a25b2907beabf8416d8a39ec867ea64024446d61b369c as base

RUN addgroup -g 999 appuser && \
    adduser -D -u 999 -G appuser -h /home/appuser appuser

USER appuser
WORKDIR /app
