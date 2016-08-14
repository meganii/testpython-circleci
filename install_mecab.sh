#!/bin/bash

# Remove mecab
sudo apt-get remove mecab

if [ -d $HOME/usr/lib/mecab ]; then
  # load mecab.so
  sudo sh -c "echo '$HOME/usr/lib' >> /etc/ld.so.conf"
  sudo ldconfig
  exit
fi

# Local Lib Directory
mkdir -p $HOME/usr/lib

# Install mecab
cd /var/tmp
curl -O https://mecab.googlecode.com/files/mecab-0.996.tar.gz
tar zxfv mecab-0.996.tar.gz
cd mecab-0.996
./configure --prefix=$HOME/usr
make
make install

# load mecab.so
sudo sh -c "echo '$HOME/usr/lib' >> /etc/ld.so.conf"
sudo ldconfig

# Install mecab-ipadic
cd /var/tmp
curl -O https://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz
tar zxfv mecab-ipadic-2.7.0-20070801.tar.gz
cd mecab-ipadic-2.7.0-20070801
./configure --with-charset=utf8 --prefix=$HOME/usr --with-mecab-config=/usr/local/bin/mecab-config
make
make DESTDIR=$HOME install

# Install mecab-python
pip install https://mecab.googlecode.com/files/mecab-python-0.996.tar.gz
