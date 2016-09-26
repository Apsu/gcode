#!/usr/bin/env python

from __future__ import print_function

from gcode import Printer
from gcode.utils import *
from gcode.constants import Extrusion


# Entry point
if __name__ == "__main__":
    try:
        p = Printer(
            nozzle_size=0.4,
            layer_height=0.2,
            retract_distance=0.8,
            retract_speed=35,
            extruder_temp=200,
            bed_temp=60
        )
        # Output i3 Mk2 startup codes
        start_mk2(p)

        # Draw 50x50 rectangle starting at 50,50
        p.rect(50, 50, 100, 100, retract=True, home=True)

        # Move to Z=5
        p.move(z=5, extrude=Extrusion.idle, comment="lift head")

        # Finish print
        stop_mk2(p)
    except ValueError as e:
        print("Incorrect value: {}".format(e))
#    except Exception as e:
#        print("Exception: {}".format(e))
#        raise e
