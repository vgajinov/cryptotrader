FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    bzip2 \
    libbz2-dev \
    liblzma-dev \
    libsqlite3-dev \
    uuid \
    uuid-dev \
    libgdbm-compat-dev \
    wget \
    tar \
    git \
    sudo \
    dbus \
    x11-apps \
    libx11-xcb-dev \
    libxkbcommon0 \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libxkbcommon-x11-dev \
    libglu1-mesa-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libx11-dev \
    libxext-dev \
    libxfixes-dev \
    libxi-dev \
    libxrender-dev \
    libxcb1-dev \
    libx11-xcb-dev \
    libxcb-glx0-dev \
    libxkbcommon-x11-dev \
    libxcb-keysyms1-dev \
    libxcb-image0-dev \
    libxcb-shm0-dev \
    libxcb-icccm4-dev \
    libxcb-sync0-dev \
    libxcb-xfixes0-dev \
    libxcb-shape0-dev \
    libxcb-randr0-dev \
    libxcb-render-util0-dev \
    libxcb-keysyms1-dev \
    libxcb-image0-dev \
    libxcb-shm0-dev \
    libxcb-icccm4-dev \
    libxcb-sync0-dev \
    libxcb-xfixes0-dev \
    libxcb-shape0-dev \
    libxcb-randr0-dev \
    libxcb-render-util0-dev \
    tk \
    tk-dev \
    tcl \
    tcl-dev \
 && rm -rf /var/lib/apt/lists/*


ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin
ENV LD_LIBRARY_PATH=

ENV LD_LIBRARY_PATH=/opt/apps/sw/python3/lib:$LD_LIBRARY_PATH
ENV PATH=/opt/apps/sw/python3/bin:$PATH
ENV PYTHONPATH=/opt/apps/sw/python3/lib/python3.7/site-packages
ENV PKG_CONFIG_PATH=/opt/apps/sw/python3/lib/pkgconfig:$PKG_CONFIG_PATH

ENV LD_LIBRARY_PATH=/opt/apps/sw/qt/qt5.12.4/lib:$LD_LIBRARY_PATH
ENV PATH=/opt/apps/sw/qt/qt5.12.4/bin:$PATH
ENV QT_XKB_CONFIG_ROOT=/usr/share/X11/xkb

ENV LD_LIBRARY_PATH=/opt/apps/sw/talib/lib:$LD_LIBRARY_PATH
ENV CFLAGS=-I/opt/apps/sw/talib/include
ENV LDFLAGS=-L/opt/apps/sw/talib/lib

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime \
 && apt-get update \
 && apt-get install -y tzdata \
 && dpkg-reconfigure --frontend noninteractive tzdata

RUN useradd -m developer -d /home/developer -c "developer user" -s /bin/bash \
 && chmod +w /etc/sudoers \
 && echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
 && chmod -w /etc/sudoers

RUN mkdir -p /opt/apps/install \
 && mkdir -p /opt/apps/sw

RUN mkdir -p /opt/apps/sw/python3 \
 && cd /opt/apps/install \
 && wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz \
 && xzcat Python-3.7.3.tar.xz | tar -xv \
 && cd Python-3.7.3 \
 && ./configure --prefix=/opt/apps/sw/python3 --enable-shared  --enable-optimizations \
 && make \
 && make install

RUN mkdir -p /opt/apps/sw/qt/qt5.12.4 \
 && cd /opt/apps/install/ \
 && wget http://download.qt.io/official_releases/qt/5.12/5.12.4/single/qt-everywhere-src-5.12.4.tar.xz \
 && xzcat qt-everywhere-src-5.12.4.tar.xz | tar -xv \
 && cd qt-everywhere-src-5.12.4 \
 && yes | ./configure --prefix=/opt/apps/sw/qt/qt5.12.4 -opensource -release  \
 && make -j8 \
 && make install


RUN mkdir -p /opt/apps/install/talib \
 && mkdir -p /opt/apps/sw/talib \
 && cd /opt/apps/install \
 && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
 && tar xzvf ta-lib-0.4.0-src.tar.gz \
 && cd /opt/apps/install/ta-lib \
 && ./configure --prefix=/opt/apps/sw/talib \
 && make \
 && make install

RUN rm -fr /opt/apps/install

RUN pip3 install \
     wheel \
     alabaster==0.7.12 \
     attrs==19.1.0 \
     Babel==2.7.0 \
     backcall==0.1.0 \
     bleach==3.1.0 \
     certifi==2019.6.16 \
     chardet==3.0.4 \
     cycler==0.10.0 \
     Cython==0.29.13 \
     decorator==4.4.0 \
     defusedxml==0.6.0 \
     docutils==0.15.2 \
     entrypoints==0.3 \
     idna==2.8 \
     imagesize==1.1.0 \
     ipykernel==5.1.1 \
     ipython==7.7.0 \
     ipython-genutils==0.2.0 \
     ipywidgets==7.5.1 \
     jedi==0.14.1 \
     Jinja2==2.10.1 \
     json5==0.8.5 \
     jsonschema==3.0.1 \
     jupyter==1.0.0 \
     jupyter-client==5.3.1 \
     jupyter-console==6.0.0 \
     jupyter-core==4.5.0 \
     jupyterlab==1.0.4 \
     jupyterlab-server==1.0.0 \
     kiwisolver==1.1.0 \
     MarkupSafe==1.1.1 \
     matplotlib==3.1.1 \
     mistune==0.8.4 \
     nbconvert==5.5.0 \
     nbformat==4.4.0 \
     notebook==6.0.0 \
     numpy==1.17.0 \
     packaging==19.1 \
     pandas==0.25.0 \
     pandocfilters==1.4.2 \
     parso==0.5.1 \
     pexpect==4.7.0 \
     pickleshare==0.7.5 \
     prometheus-client==0.7.1 \
     prompt-toolkit==2.0.9 \
     ptyprocess==0.6.0 \
     Pygments==2.4.2 \
     pyparsing==2.4.2 \
     PyQt5==5.12.3 \
     PyQt5-sip==4.19.18 \
     pyrsistent==0.15.4 \
     python-dateutil==2.8.0 \
     pytz==2019.2 \
     pyzmq==18.0.2 \
     qtconsole==4.5.2 \
     requests==2.22.0 \
     scipy==1.3.0 \
     Send2Trash==1.5.0 \
     six==1.12.0 \
     snowballstemmer==1.9.0 \
     Sphinx==2.1.2 \
     sphinx-bootstrap-theme==0.7.1 \
     sphinxcontrib-applehelp==1.0.1 \
     sphinxcontrib-devhelp==1.0.1 \
     sphinxcontrib-htmlhelp==1.0.2 \
     sphinxcontrib-jsmath==1.0.1 \
     sphinxcontrib-qthelp==1.0.2 \
     sphinxcontrib-serializinghtml==1.1.3 \
     terminado==0.8.2 \
     testpath==0.4.2 \
     tornado==6.0.3 \
     traitlets==4.3.2 \
     urllib3==1.25.3 \
     wcwidth==0.1.7 \
     webencodings==0.5.1 \
     widgetsnbextension==3.5.1 \
     PyDispatcher==2.0.5 \
     requests==2.22.0 \
     websocket==0.2.1 \
     websocket-client==0.56.0 \
     pyqtgraph==0.10.0 \
     PyQtChart==5.12 \
     TA-lib==0.4.17 \
     elasticsearch==7.0.2

# map the dir of the project from the host to the container
# using the flag e.g -v $HOME/cryptotrader:/home/developer/cryptotrader
RUN mkdir /home/developer/cryptotrader

RUN apt-get clean

USER developer
WORKDIR /home/developer

CMD ["bash"]

