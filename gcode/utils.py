from constants import *


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

def extrusion(printer, distance):
    "Get filament distance for move distance"

    # Store values
    f = printer.filament_diameter
    fr = f / 2
    e = printer.extrusion_multiplier
    n = printer.nozzle_size
    h = printer.layer_height
    hr = h / 2
    w = printer.line_width

    # Calculate capsule cross-section of filament
    #   See http://manual.slic3r.org/advanced/flow-math
    area = (w - h)*h + pi*(hr)**2

    # Volume of line
    volume = area * distance

    # Filament length, scaled by extrusion multiplier
    #   length mm = capsule mm^3 / filament mm^2
    length = volume/(pi*fr**2)*e

    # Return length for extruder
    return length

def write(code, comment=None, **kwargs):
    "Write command with args"

    # Start with G/M Code
    command = code

    # Convert args to prefixes and values
    args = [
        "{}{}".format(k.upper(), v)
        for k, v in kwargs.items()
    ]

    # Format and add args if any
    if len(args):
        command += " " + " ".join(args)

    # Add comment if provided
    if comment:
        command += " ; {}".format(comment)

    # Print to stdout
    print(command)

def start_mk2(printer):
    """
    Write out starting codes

    This sequences is for the Original Prusa i3 Mk2
    """

    # Set units to millimeters
    printer.units = Units.mm
    # Set absolute positioning
    printer.positioning = Offsets.absolute
    # Set relative extrusion
    printer.extruding = Offsets.relative
    # Home axes without MBL
    printer.home(axes=["w"], comment="home without Z leveling")
    #write("G28", "home without leveling", w="")

    # Start heating and continue
    printer.heat()

    # Perform MBL
    printer.level_mk2()
    #write("M80", "perform mesh bed leveling")

    # Store position; z = 0.15 after leveling
    #printer.position = {"x": 0, "y": 0, "z": 0.15}

    # Finish heating and wait
    printer.heat(wait=True)

    # Go outside print area
    #printer.feed_rate = 1000
    printer.move(y=-3.0, comment="move outside print area", extrude=Extrusion.idle, rate=1000)

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

def stop_mk2(printer):
    "Output commands to finish print"

    # Turn off heaters
    printer.heat(0, 0)

    # Turn off part fan
    printer.fan = 0
    #write("M107", comment="turn off fan")

    # Turn off steppers
    printer.idle()
    #write("M84", comment="turn off steppers")
