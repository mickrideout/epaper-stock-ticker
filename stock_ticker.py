#!/usr/bin/env python3
import argparse
import importlib
import logging
import os
import sys
import time

import yfinance as yf
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, 'e-Paper', 'RaspberryPi_JetsonNano', 'python', 'lib')
FONT_PATH = os.path.join(BASE_DIR, 'e-Paper', 'RaspberryPi_JetsonNano', 'python', 'pic', 'Font.ttc')

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)


def fit_font(text, max_width, max_height, font_path, start_size=300):
    size = start_size
    while size > 8:
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            return font, w, h
        size -= 4
    font = ImageFont.truetype(font_path, 8)
    bbox = font.getbbox(text)
    return font, bbox[2] - bbox[0], bbox[3] - bbox[1]


def get_daily_change(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='5d')
    if len(hist) < 2:
        logger.warning("Insufficient history for %s", symbol)
        return None, None, None
    prev_close = hist['Close'].iloc[-2]
    last_close = hist['Close'].iloc[-1]
    change = last_close - prev_close
    pct = (change / prev_close) * 100
    return last_close, change, pct


def build_images(epd, symbol, last_price, change, pct):
    width = epd.width
    height = epd.height

    black_img = Image.new('1', (width, height), 255)
    red_img = Image.new('1', (width, height), 255)

    draw_black = ImageDraw.Draw(black_img)

    upper_height = int(height * 0.55)
    lower_height = height - upper_height

    padding = 20

    ticker_font, tw, th = fit_font(
        symbol,
        width - padding * 2,
        upper_height - padding * 2,
        FONT_PATH,
    )
    ticker_x = (width - tw) // 2
    ticker_y = (upper_height - th) // 2
    draw_black.text((ticker_x, ticker_y), symbol, font=ticker_font, fill=0)

    change_text = f'{change:+.2f}  {pct:+.2f}%'

    change_font, cw, ch = fit_font(
        change_text,
        width - padding * 2,
        lower_height - padding * 2,
        FONT_PATH,
    )

    change_x = (width - cw) // 2
    change_y = upper_height + (lower_height - ch) // 2

    if change < 0:
        draw_red = ImageDraw.Draw(red_img)
        draw_red.text((change_x, change_y), change_text, font=change_font, fill=0)
    else:
        draw_black.text((change_x, change_y), change_text, font=change_font, fill=0)

    return black_img, red_img


def display_ticker(epd, symbol):
    logger.info("Fetching data for %s", symbol)
    last_price, change, pct = get_daily_change(symbol)

    if last_price is None:
        logger.error("Could not fetch data for %s, skipping", symbol)
        return

    logger.info("%s  last=%.2f  change=%+.2f  pct=%+.2f%%", symbol, last_price, change, pct)

    black_img, red_img = build_images(epd, symbol, last_price, change, pct)

    logger.info("Initialising display for %s", symbol)
    epd.init()
    epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
    epd.sleep()
    logger.info("Display updated for %s", symbol)


def parse_args():
    parser = argparse.ArgumentParser(description='E-paper stock ticker display')
    parser.add_argument(
        '--tickers',
        required=True,
        help='Comma-separated list of ticker symbols, e.g. AAPL,GOOG,TSLA',
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=5.0,
        help='Minutes to display each ticker (default: 5)',
    )
    parser.add_argument(
        '--driver',
        required=True,
        help='Waveshare EPD driver module name, e.g. epd7in5b_V2',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    tickers = [t.strip().upper() for t in args.tickers.split(',') if t.strip()]
    duration_seconds = args.duration * 60

    logger.info("Loading driver: waveshare_epd.%s", args.driver)
    epd_module = importlib.import_module(f'waveshare_epd.{args.driver}')
    epd = epd_module.EPD()

    logger.info("Tickers: %s  Duration: %.1f min each", tickers, args.duration)

    try:
        while True:
            for symbol in tickers:
                display_ticker(epd, symbol)
                logger.info("Sleeping for %.1f minutes before next ticker", args.duration)
                time.sleep(duration_seconds)
    except KeyboardInterrupt:
        logger.info("Interrupted — putting display to sleep")
        try:
            epd.init()
            epd.sleep()
        except Exception:
            pass
        sys.exit(0)


if __name__ == '__main__':
    main()
