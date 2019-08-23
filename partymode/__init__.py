import bhi160
import display
import utime
import buttons
import leds
import os

from color import Color

disp = display.open()
sensor = 0

sensors = [
    # {"sensor": bhi160.BHI160Orientation(), "name": "Orientation"},
    {"sensor": bhi160.BHI160Accelerometer(), "name": "Accelerometer"},
    {"sensor": bhi160.BHI160Gyroscope(), "name": "Gyroscope"},
]

subtractors = [0.5, 128]

battery_color_good = [  0,230,0]
battery_color_ok   = [255,215,0]
battery_color_bad  = [255,  0,0]

def get_bat_color():
    """
    Function determines the color of the battery indicator. Colors can be set in config.
    Voltage threshold's are currently estimates as voltage isn't that great of an indicator for
    battery charge.
    :return: false if old firmware, RGB color array otherwise
    """
    try:
        v = os.read_battery()
        if v > 3.8:
            return battery_color_good
        if v > 3.6:
            return battery_color_ok
        return battery_color_bad
    except AttributeError:
        return False


def render_battery(disp):
    """
    Adds the battery indicator to the display. Does not call update or clear so it can be used in addition to
    other display code.
    :param disp: open display
    """
    c = get_bat_color()
    if not c:
        return
    disp.rect(140, 2, 155, 9, filled=True, col=c)
    disp.rect(155, 4, 157, 7, filled=True, col=c)
    try:
        v = os.read_battery()
        disp.print("{:.4} V".format(v), posy=40, fg=c)
        if v < 4.0:
            disp.rect(151, 3, 154, 8, filled=True, col=[0,0,0])
        if v < 3.8:
            disp.rect(146, 3, 151, 8, filled=True, col=[0,0,0])
        if v < 3.6:
            disp.rect(141, 3, 146, 8, filled=True, col=[0,0,0])
    except AttributeError:
        return

while True:
    # Read and print sample
    samples = sensors[sensor]["sensor"].read()
    if len(samples) > 0:
        disp.clear()
        sample = samples[0]

        color = [255, 0, 0]
        if sample.status == 1:
            color = [255, 128, 0]
        elif sample.status == 2:
            color = [255, 255, 0]
        elif sample.status == 3:
            color = [0, 200, 0]

        subtractor = subtractors[sensor]

        colors = [abs(s) - subtractor for s in [sample.x, sample.y, sample.z]]
        display_colors = [0 if c < 0 else 255 for c in colors]

        new_color = Color(*display_colors)

        render_battery(disp)

        disp.update()

        leds.set_all([new_color for _ in range(11)])
       
    # Read button
    v = buttons.read(buttons.BOTTOM_RIGHT)
    if v == 0:
        button_pressed = False

    if not button_pressed and v & buttons.BOTTOM_RIGHT != 0:
        button_pressed = True
        sensor = (sensor + 1) % len(sensors)
