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


def main():

    # setup rgbmatrix
    matrix = setup_matrix()
    
    # canvas: the thing you draw on
    canvas = matrix.CreateFrameCanvas()


    font = graphics.Font()
    font.LoadFont("fonts/tahoma-10.bdf")

    # get api data by calling our tracker api wrapper
    bbox = BBOXES['pres']

    print("loop starting")
    while True:
        try:
            canvas.Fill(0,0,0)
            now = time.time()
            lines = tracker_api_adapter.get_next_trips_from_bbox(bbox, 3)

            # do something with the data
            for i, line in enumerate(lines):
                # colored number
                graphics.DrawText(canvas, font, 1, 7 + 10*i, color(line.routeColor, hex=True), line.routeName)

                # headsign
                graphics.DrawText(canvas, font, 18, 7 + 10*i, COLOR_WHITE, line.headsign[:6])

                # ETA
                eta_num = line.arrivalTime - now
                eta_str = tracker_api_adapter.convert_duration_to_eta_3(eta_num)
                eta_str_len = graphics.MeasureText(font, eta_str)
                graphics.DrawText(canvas, font, canvas.width - eta_str_len - 1, 8 + 10*i, COLOR_WHITE, eta_str)

                if eta_num < 600:
                    graphics.DrawText(canvas, font, canvas.width - eta_str_len - 1, 8 + 10*i, color("0,200,200"), eta_str)
                else:
                    graphics.DrawText(canvas, font, canvas.width - eta_str_len - 1, 8 + 10*i, COLOR_WHITE, eta_str)

            # when the canvas is ready to be shown
            canvas = matrix.SwapOnVSync(canvas)

            time.sleep(30)

        except KeyboardInterrupt:
            sys.exit(0)

        # except Exception:
        #     sys.exit(1)


if __name__ == "__main__":
    main()


