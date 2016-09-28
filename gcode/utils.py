from constants import *
from math import sqrt


def mms_to_mmm(mms):
    "Convert mm/s to mm/min"

    return mms*60

def distance(x, y):
    "Get pythagorean distance for offsets"

    if x == 0:
        return y
    elif y == 0:
        return x
    else:
        return sqrt(x**2 + y**2)

def write(code, *args, **kwargs):
    "Write command with args"

    # Start with G/M Code
    command = code

    # Extract comment if present
    comment = None
    if "comment" in kwargs:
        comment = kwargs["comment"]
        del kwargs["comment"]

    # Convert kwargs to prefixes and values
    params = [
        "{}{}".format(k.upper(), v)
        for k, v in kwargs.items()
    ]

    # Convert args to prefixes if any
    if len(args):
        command += " " + "".join(map(lambda x:x.upper(), args))

    # Format and add params if any
    if len(params):
        command += " " + " ".join(params)

    # Add comment if provided
    if comment:
        command += " ; {}".format(comment)

    # Print to stdout
    print(command)

def start_mk2(printer):
    """
    Write out starting codes

    This sequence is for the Original Prusa i3 Mk2
    """

    # Set units to millimeters
    printer.units = Units.mm
    # Set absolute positioning
    printer.positioning = Offsets.absolute
    # Set relative extrusion
    printer.extruding = Offsets.relative
    # Home axes without MBL
    printer.home(axes=["w"], comment="home without Z leveling")

    # Start heating and continue
    printer.heat()

    # Perform MBL
    printer.level_mk2()

    # Finish heating and wait
    printer.heat(wait=True)

    # Go outside print area
    printer.move(y=-3.0, comment="move outside print area", extrude=Extrusion.idle, rate=17)

    # Store line width
    line_width = printer.line_width

    # Print thick intro line
    printer.line_width = 1.85
    printer.move(x=60, comment="print first wipe line")

    # Print thicker intro line
    printer.line_width = 3.8
    printer.move(x=100, comment="print second wipe line")

    # Restore line width
    printer.line_width = line_width

    # Go to defined layer height
    printer.move(z=printer.layer_height, comment="move to initial layer height", extrude=Extrusion.idle, rate=100)

def stop_mk2(printer):
    "Output commands to finish print"

    # Turn off heaters
    printer.heat(0, 0)

    # Turn off part fan
    printer.fan = 0

    # Turn off steppers
    printer.idle()
