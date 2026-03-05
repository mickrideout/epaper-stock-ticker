# epaper-stock-ticker

## Installation

```
git clone --recurse-submodules https://github.com/mickrideout/epaper-stock-ticker.git
sudo apt update
sudo apt install python3-venv
python3 -m venv epaperenv --system-site-packages
source epaperenv/bin/activate
cd epaper-stock-ticker
sudo apt-get update
sudo apt-get install libjpeg-dev zlib1g-dev libopenblas-dev python3-spidev libfreetype6-dev libjpeg-dev build-essential python3-numpy python3-pandas python3-pil
pip install -r requirements.txt --prefer-binary --extra-index-url https://www.piwheels.org/simple
```

## Run

```
python stock_ticker.py --driver epd7in5b_V2 --duration 15 --tickers GC=F,SGLP.L,XMWX.L,EXUS.AX
```
