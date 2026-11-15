import time
import sys
import argparse

import tracker_api_adapter

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
    BBOX_STUDIO_ARTS = "-72.524341,42.387466,-72.522960,42.388068"
    lines = tracker_api_adapter.get_next_trips_from_bbox(BBOX_STUDIO_ARTS, 3)

    # do something with the data
    for i, line in enumerate(lines):
        graphics.DrawText(canvas, font, 1, 7 + 10*i, COLOR_WHITE, line.routeName)
        graphics.DrawText(canvas, font, 18, 7 + 10*i, COLOR_WHITE, line.headsign)

    # when the canvas is ready to be shown
    canvas = matrix.SwapOnVSync(canvas)

    try:
        print("Press CTRL-C to stop.")
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        sys.exit(0)




def screen_onebyone(matrix):

    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()

    # colors made by calling color("r,g,b")
    canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

    # get api data by calling our tracker api wrapper
    BBOX_STUDIO_ARTS = "-72.524341,42.387466,-72.522960,42.388068"

    now = time.time()
    lines = tracker_api_adapter.get_next_trips_from_bbox(BBOX_STUDIO_ARTS, 3)

    # do something with the data
    fontmain = graphics.Font()
    fontmain.LoadFont(f"fonts/tahoma-15.bdf")

    fontmedium = graphics.Font()
    fontmedium.LoadFont(f"fonts/tahoma-12.bdf")

    fontsmall = graphics.Font()
    fontsmall.LoadFont(f"fonts/tahoma-9.bdf")

    total_switches = 0
    while True:
        line = lines[total_switches % 3]
        eta_str = tracker_api_adapter.convert_duration_to_eta(line.arrivalTime - now)

        ticks_per_screen = 2000
        i = ticks_per_screen

        scroll_increment = .08
        x_pos = int(canvas.width * .6)
        x_pos2 = canvas.width

        while i > 0:
            canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

            graphics.DrawText(canvas, fontmain, 1, 15, COLOR_WHITE, line.routeName)
            graphics.DrawText(canvas, fontmedium, 40, 15, COLOR_WHITE, eta_str)

            x_pos -= scroll_increment
            len = graphics.DrawText(canvas, fontsmall, x_pos, 26, COLOR_WHITE, line.headsign)
            if x_pos + len < canvas.width / 1.7:
                graphics.DrawText(canvas, fontsmall, x_pos2, 26, COLOR_WHITE, line.headsign)
                x_pos2 -= scroll_increment
            elif x_pos + len < 0:
                x_pos = canvas.width
                x_pos2 = canvas.width

            bar_width = int(canvas.width * (float(i) / ticks_per_screen))
            graphics.DrawLine(canvas, 0, canvas.height-2, bar_width, canvas.height-2, COLOR_WHITE)
            graphics.DrawLine(canvas, 0, canvas.height-1, bar_width, canvas.height-1, COLOR_WHITE)

            # when the canvas is ready to be shown
            canvas = matrix.SwapOnVSync(canvas)

            i -= 1
        total_switches += 1

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
    elif args.screen == "1x1":
        screen_onebyone(matrix)


if __name__ == "__main__":
    main()


