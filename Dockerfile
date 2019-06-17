FROM ubuntu:19.04

# Prepare the system for forwarding host X server staff to the docker image
# -------------------------------------------------------------------------------------

# Create sudoers file and sudoers.d directory if not present
RUN [ ! -f /etc/sudoers ] && echo "#includedir /etc/sudoers.d" >> /etc/sudoers && \
    mkdir /etc/sudoers.d

# Create a new user (i.e. developer) and added to sudoers
# Replace 1000 with your user / group id on the host system
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer


# Install Qt, TA-lib and the rest of dependencies
# -------------------------------------------------------------------------------------
    
RUN echo "deb http://archive.ubuntu.com/ubuntu/ disco universe" | sudo tee -a /etc/apt/sources.list;    \
    apt update && apt install -y   \
        build-essential     \
        wget                \
        tar                 \
        git                 \
        qt5-default         \
        qt5-qmake           \
        libqt5webkit5-dev   \
        python              \
        python3             \
        python3-pip         \
    && rm -rf /var/lib/apt/lists/*


RUN mkdir talib && cd talib && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz;     \
    tar xzvf ta-lib-0.4.0-src.tar.gz ;    \
    cd ta-lib && ./configure ;            \
    make && make install ;                

    
# Install python packages
# -------------------------------------------------------------------------------------

RUN pip3 install --force-reinstall    \
        sip                 \
        wheel               \
        pydispatcher        \
        urllib3             \
        requests            \
        websocket           \
        websocket-client    \
        pyqt5==5.12.2       \
        pyqtgraph           \
        PyQtChart           \
        TA-lib


# Get the repository
# -------------------------------------------------------------------------------------

# NOTE: you must provide your github credentials
RUN mkdir autotrader && cd autotrader &&    \
    git clone https://<user>:<password>@github.com/mherkazandjian/autotrader.git . ;


CMD cd autotrader && LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib QT_QPA_PLATFORM=offscreen python3 ATGui.py
