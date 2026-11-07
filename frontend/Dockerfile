
# Stage 1: Build
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

# Install React plugin compatible with Vite 7
RUN npm install -D @vitejs/plugin-react@^5.0.0

COPY . .

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Stage 2: Production
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
