import time
import sys
import argparse

import tracker_api_adapter

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


BBOXES = {
    "springfieldunion" : "-72.596326,42.105475,-72.593473,42.107178",
    "studioarts" : "-72.524341,42.387466,-72.522960,42.388068",
    "haigismall" : "-72.527109,42.386394,-72.525301,42.387728",
    "pres" : "-72.529501,42.403016,-72.528851,42.403332",
    "cowleslane" : "-72.520264,42.377611,-72.519439,42.378079"
}


def color(value, hex=False):
    if hex:
        value = ",".join(str(int(value[i:i+2], 16)) for i in range(3))
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



def screen_3up(matrix, bbox_name):
    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()

    # colors made by calling color("r,g,b")
    canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

    # get api data by calling our tracker api wrapper
    bbox = BBOXES[bbox_name]

    num_trips = 3

    font = graphics.Font()
    font.LoadFont("fonts/tahoma-10.bdf")

    try:
        print("loop starting, ctrl+c to stop...")

        ticks_per_screen = 1600
        i = 0
        page = 0
        while True:
            if i == 0:
                i = ticks_per_screen
                page += 1
                now = time.time()
                lines = tracker_api_adapter.get_next_trips_from_bbox(bbox, num_trips)
            for row, line in enumerate(lines):
                if page % 2 == 1:
                    graphics.DrawText(canvas, font, 1, 8*row, color(line.routeColor, hex=True), line.routeName)
                else:                    
                    graphics.DrawText(canvas, font, 1, 8*row, color(line.routeColor, hex=True), line.headsign)
                
                eta_str = tracker_api_adapter.convert_duration_to_eta_3(line.arrivalTime - now)
                eta_str_len = graphics.MeasureText(font, eta_str)
                graphics.DrawText(canvas, font, canvas.width - eta_str_len - 1, 8 + 10*i, COLOR_WHITE, eta_str)
            canvas = matrix.SwapOnVSync(canvas)
            i -= 1

    except KeyboardInterrupt:
        sys.exit(0)




def screen_onebyone(matrix, bbox_name):

    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()

    # colors made by calling color("r,g,b")
    canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

    # get api data by calling our tracker api wrapper
    bbox = BBOXES[bbox_name]

    num_trips = 5

    now = time.time()
    lines = tracker_api_adapter.get_next_trips_from_bbox(bbox, num_trips)

    # do something with the data
    fontmain = graphics.Font()
    fontmain.LoadFont(f"fonts/tahoma-15.bdf")

    fontmedium = graphics.Font()
    fontmedium.LoadFont(f"fonts/tahoma-12.bdf")

    fontsmall = graphics.Font()
    fontsmall.LoadFont(f"fonts/tahoma-9.bdf")

    total_switches = 0
    try:
        print("loop starting, ctrl+c to stop...")
        while True:
            line = lines[total_switches % min(len(lines), num_trips)]
            hrs, mins = tracker_api_adapter.convert_duration_to_eta_2(line.arrivalTime - now)

            ticks_per_screen = 2000
            i = ticks_per_screen

            scroll_increment = .08
            x_pos = int(canvas.width * .6)
            x_pos2 = canvas.width

            while i > 0:
                canvas.Fill(COLOR_BLACK.red, COLOR_BLACK.green, COLOR_BLACK.blue)

                graphics.DrawText(canvas, fontmain, 3, 14, color(line.routeColor, hex=True), line.routeName)

                eta_m_len = graphics.MeasureText(fontsmall, 'm')
                eta_mins_len = graphics.MeasureText(fontmedium, mins) + eta_m_len
                graphics.DrawText(canvas, fontsmall, canvas.width - eta_m_len - 3, 14, COLOR_WHITE, 'm')
                graphics.DrawText(canvas, fontmedium, canvas.width - eta_mins_len - 3, 14, COLOR_WHITE, mins)
                if hrs != "0":
                    eta_h_len = graphics.MeasureText(fontsmall, 'h') + eta_mins_len + 2
                    eta_hrs_len = graphics.MeasureText(fontmedium, hrs) + eta_h_len
                    graphics.DrawText(canvas, fontsmall, canvas.width - eta_h_len - 3, 14, COLOR_WHITE, 'h')
                    graphics.DrawText(canvas, fontmedium, canvas.width - eta_hrs_len - 3, 14, COLOR_WHITE, hrs)

                x_pos -= scroll_increment
                scroll_len = graphics.DrawText(canvas, fontsmall, x_pos, 26, COLOR_WHITE, line.headsign)
                if x_pos + scroll_len < canvas.width / 1.7:
                    graphics.DrawText(canvas, fontsmall, x_pos2, 26, COLOR_WHITE, line.headsign)
                    x_pos2 -= scroll_increment
                elif x_pos + scroll_len < 0:
                    x_pos = canvas.width
                    x_pos2 = canvas.width

                bar_width = int(canvas.width * (float(i) / ticks_per_screen))
                graphics.DrawLine(canvas, 0, canvas.height-1, bar_width, canvas.height-1, COLOR_WHITE)

                # when the canvas is ready to be shown
                canvas = matrix.SwapOnVSync(canvas)

                i -= 1
            total_switches += 1
    except KeyboardInterrupt:
        sys.exit(0)




def main():

    # arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("screen")
    parser.add_argument("bbox_name")
    args = parser.parse_args()

    # setup rgbmatrix
    matrix = setup_matrix()
    
    # choose screen to show
    if args.screen == "3ups":
        screen_3upsimple(matrix, args.bbox_name)
    if args.screen == "3up":
        screen_3up(matrix, args.bbox_name)
    elif args.screen == "1x1":
        screen_onebyone(matrix, args.bbox_name)


if __name__ == "__main__":
    main()


