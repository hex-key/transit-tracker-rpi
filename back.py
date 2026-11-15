import time
import sys
import argparse

import tracker

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


global font

def color(value):
    try:
        return graphics.Color(*[int(v) for v in value.split(",")])
    except:
        print(f"invalid color value: {value}")
        exit(1)

COLOR_BLACK = color("0,0,0")
COLOR_WHITE = color("255,255,255")

def setup_matrix():
    # Configuration for the matrix
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.gpio_slowdown = 3
    options.brightness = 40
    options.drop_privileges = False
    #options.chain_length = 1
    #options.parallel = 1
    options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

    return RGBMatrix(options = options)


def screen_3upsimple(matrix):

    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()

    # colors made by calling color("r,g,b")
    canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

    # get api data by calling our tracker api wrapper
    lines = tracker.get_board_lines()

    # do something with the data
    for i, line in enumerate(lines):
        graphics.DrawText(canvas, font, 1, 7 + 10*i, COLOR_WHITE, line[0])
        graphics.DrawText(canvas, font, 18, 7 + 10*i, COLOR_WHITE, line[1])

    # when the canvas is ready to be shown
    canvas = matrix.SwapOnVSync(canvas)

    try:
        print("Press CTRL-C to stop.")
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        sys.exit(0)





def main():

    # arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("screen")
    parser.add_argument("-f", "--font", type=str, default='6x9')
    args = parser.parse_args()

    global font
    font = graphics.Font()
    font.LoadFont(f"fonts/{args.font}.bdf")

    # setup rgbmatrix
    matrix = setup_matrix()
    
    # choose screen to show
    if args.screen == "3up":
      screen_3upsimple(matrix)


if __name__ == "__main__":
    main()


