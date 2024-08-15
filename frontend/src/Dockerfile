FROM node:21

WORKDIR /frontend
COPY package*.json ./

# Install dependencies
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
EXPOSE 3000

CMD ["serve", "-s", "build"]
