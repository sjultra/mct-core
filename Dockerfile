from ubuntu:latest

WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y curl sudo wget unzip python3 python3-pip git 

RUN wget https://releases.hashicorp.com/terraform/1.4.4/terraform_1.4.4_linux_amd64.zip -O terraform.zip && \
    unzip terraform.zip && \
    install -o root -g root -m 0755 terraform /usr/local/bin/terraform

RUN curl -fsSL https://deb.nodesource.com/setup_19.x | bash - &&apt-get install -y nodejs

RUN npm install --global cdktf-cli@latest

RUN pip3 install --upgrade pip wheel setuptools requests pipenv

WORKDIR /root
