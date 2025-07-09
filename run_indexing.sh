#!/bin/bash

java \
    -Djava.util.logging.config.file=/opengrok/etc/logging.properties \
    -jar /opengrok/dist/lib/opengrok.jar \
    -t 4 \
    -c /usr/local/bin/ctags \
    -s /opengrok/src -d /opengrok/data -H -S -G \
    -p __all__ \
    -W /opengrok/etc/configuration.xml -U http://localhost:8080/opengrok
