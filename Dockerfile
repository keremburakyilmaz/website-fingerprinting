FROM node:24-alpine

WORKDIR /app

RUN apk add --update --no-cache \
    make \
    g++ \
    python3 \
    py3-setuptools \
    py3-pip

COPY package*.json ./

RUN npm ci 

COPY . .

CMD ["npm", "start"]
