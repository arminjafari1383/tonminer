
# مرحله اول: Build فرانت‌اند
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./

# نصب وابستگی‌ها
RUN npm ci

# نصب پلاگین React در صورت نبودن در package.json
RUN npm install -D @vitejs/plugin-react

COPY . .

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

# ساخت نسخه Production
RUN npm run build

# مرحله دوم: اجرای Production با Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
