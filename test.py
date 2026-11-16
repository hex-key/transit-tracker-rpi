import time
import sys
import argparse

import tracker_api_adapter

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


global font

BBOXES = {
    "springfieldunion" : "-72.596326,42.105475,-72.593473,42.107178",
    "studioarts" : "-72.524341,42.387466,-72.522960,42.388068",
    "haigismall" : "-72.527109,42.386394,-72.525301,42.387728",
    "pres" : "-72.529501,42.403016,-72.528851,42.403332",
    "cowleslane" : "-72.520264,42.377611,-72.519439,42.378079"
}

def color(value):
    try:
        return graphics.Color(*[int(v) for v in value.split(",")])
    except:
        print(f"invalid color value: {value}")
        exit(1)

def hex2rgb(s):
    return ",".join(str(int(s[i:i+2], 16)) for i in range(3))


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


def screen_3upsimple(matrix, bbox_name):

    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()

    # colors made by calling color("r,g,b")
    canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

    # get api data by calling our tracker api wrapper
    bbox = BBOXES[bbox_name]
    lines = tracker_api_adapter.get_next_trips_from_bbox(bbox, 3)

    font = graphics.Font()
    font.LoadFont("fonts/tahoma-10.bdf")

    # do something with the data
    for i, line in enumerate(lines):
        graphics.DrawText(canvas, font, 1, 7 + 10*i, color(line.routeColor, hex=True), line.routeName)
        graphics.DrawText(canvas, font, 18, 7 + 10*i, COLOR_WHITE, line.headsign)

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


