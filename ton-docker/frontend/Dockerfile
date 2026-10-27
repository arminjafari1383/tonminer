FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 9000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9000"]
