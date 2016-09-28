#!/usr/bin/env python

from __future__ import print_function

from gcode import Printer
from gcode.utils import *
from gcode.constants import Extrusion


# Entry point
if __name__ == "__main__":
    try:
        p = Printer(
            bed_x=250,
            bed_y=210,
            nozzle_size=0.4,
            layer_height=0.2,
            retract_distance=0.8,
            retract_speed=35,
            extruder_temp=200,
            bed_temp=60
        )
        # Output i3 Mk2 startup codes
        start_mk2(p)

        # Print thicker lines for rect
        p.line_width = 1.0

        # 100mm rectangle
        size = 100

        # Center it
        x1 = (p.bed_x - size) / 2
        x2 = (p.bed_x + size) / 2
        y1 = (p.bed_y - size) / 2
        y2 = (p.bed_y + size) / 2

        # Hop to it
        p.hop(x=x1, y=y1, height=0.1, comment="move to lower left of rect", rate=100)

        # Draw 50x50 rectangle starting at 50,50
        p.rect(x1, y1, x2, y2, rate=20)

        # How many lines
        count = 20

        # Line spacing
        step = size / count

        # Draw count lines every size/count mm
        for x in range(x1+step, x2, step):
            # Hop to start
            p.hop(x=x, y=y1, height=0.1, comment="move to start of line", rate=50)
            # Print the line
            p.move(x=x, y=y2, comment="print line", extrude=Extrusion.extrude, rate=20)
            # Swap line ends
            y1, y2 = y2, y1
            # Increase Z offset for same layer height
            p.move(z=p.position["z"]-0.01, comment="adjust Z offset", extrude=Extrusion.idle, rate=100)

        # Go home
        p.move(0, 200, 5, comment="go home and up", extrude=Extrusion.retract_only, rate=100)

        # Finish print
        stop_mk2(p)
    except ValueError as e:
        print("Incorrect value: {}".format(e))
#    except Exception as e:
#        print("Exception: {}".format(e))
#        raise e
