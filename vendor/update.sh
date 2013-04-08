#!/bin/sh
set -eu

# CryptoJS - https://code.google.com/p/crypto-js/
version=3.1.2
rm -rf CryptoJS
mkdir CryptoJS
(
    cd CryptoJS
    wget "https://crypto-js.googlecode.com/files/CryptoJS%20v$version.zip" -O CryptoJS.zip
    unzip -jo CryptoJS.zip rollups/sha256.js rollups/ripemd160.js
    rm -f CryptoJS.zip
)

# "Fork me on GitHub" ribbon - https://github.com/blog/273-github-ribbons
rm -r GitHub
mkdir GitHub
(
    cd GitHub
    wget https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png
)

echo OK
