FROM debian:latest
RUN apt-get update && apt-get install -y \
    gcc \
    cmake \
    make \
    wget \
    unzip

WORKDIR /app

RUN wget https://www.sqlite.org/2018/sqlite-amalgamation-3260000.zip \
    && unzip sqlite-amalgamation-3260000.zip \
    && mkdir -p sqlite-src \
    && mv sqlite-amalgamation-3260000 sqlite-src/sqlite-amalgamation-3260000 \
    && rm sqlite-amalgamation-3260000.zip

COPY CMakeLists.txt /app/

RUN mkdir build
RUN mkdir output

WORKDIR /app/build
RUN cmake .. && make

CMD ["cp", "sqlite3.so", "/output/"]
