FROM node:24 AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:24 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN npm run build

FROM node:24 AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder --chown=node:node /app/public ./public

RUN mkdir .next
RUN chown node:node .next

COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node

# COPY --from=builder /app/.next ./.next
# COPY --from=builder /app/package*.json ./
# COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
# CMD ["npm", "run", "start"]
CMD ["node", "server.js"]
