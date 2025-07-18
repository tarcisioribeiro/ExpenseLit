FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && \
    apt-get install -y locales tzdata && \
    locale-gen pt_BR.UTF-8 && \
    update-locale LANG=pt_BR.UTF-8 && \
    echo "LANG=pt_BR.UTF-8" >> /etc/default/locale && \
    echo "keyboard-configuration  keyboard-configuration/layoutcode  select  br" | debconf-set-selections && \
    echo "keyboard-configuration  keyboard-configuration/modelcode  select  abnt2" | debconf-set-selections && \
    echo "keyboard-configuration  keyboard-configuration/variantcode  select  " | debconf-set-selections && \
    ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    keyboard-configuration console-setup \
    python3.10 python3-pip netcat curl wget nano && \
    apt-get clean

ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8
ENV TZ=America/Sao_Paulo

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8551

CMD ["streamlit", "run", "main.py", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false", "--server.port=8551", "--server.address=0.0.0.0"]
