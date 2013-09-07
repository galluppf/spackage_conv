#!/bin/sh

autoreconf --install && ./configure && make && cp src/spikeserver ./

