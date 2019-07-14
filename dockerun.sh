#!/bin/bash

docker run \
    -v $PWD:/work \
    -w /work \
    -e APCA_API_KEY_ID=PK5UMWK9NV410CUMRX4I \
    -e APCA_API_SECRET_KEY=/t4Y9LCpOklOCDTb2c/WkTVH51VtSgajhKObZSnu \
    -e APCA_API_BASE_URL=https://paper-api.alpaca.markets \
    alpacamarkets/pylivetrader pylivetrader run -f pytrader.py
