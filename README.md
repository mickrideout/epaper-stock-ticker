# epaper-stock-ticker

## Installation

```
git clone --recurse-submodules https://github.com/mickrideout/epaper-stock-ticker.git
sudo apt update
sudo apt install python3-venv
python3 -m venv epaperenv
source epaperenv/bin/activate
cd epaper-stock-ticker
sudo apt-get update
sudo apt-get install libjpeg-dev zlib1g-dev libopenblas-dev python3-spidev libfreetype6-dev libjpeg-dev build-essential
pip install -r requirements.txt
```

## Run

```
python stock_ticker.py --duration 5 --driver epd7in5b_V2 --tickers GC=F,SGLP.L,XMWX.L
```