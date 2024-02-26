FROM ubuntu

# install software dependencies
RUN apt-get update
RUN apt-get install -y vim python3 python3-pip

RUN pip3 install antlr4-tools
RUN yes | antlr4
RUN pip3 install antlr4-python3-runtime

# cleanup the installs
RUN apt-get clean
RUN rm -r /var/lib/apt/lists/*

WORKDIR /root

RUN date > /lewis_antlr_container_build_date.txt

