#!/usr/bin/env python

from __future__ import print_function
from math import pi, sqrt


class GCode(object):
    "GCode command generator"

    def __init__(
            self,
            nozzle_size=0.4,
            filament_diameter=1.75,
            layer_height=0.2,
            line_width=None,
            extruder_temp=190,
            bed_temp=0
        ):
        # XYZ position matrix
        self.position = {"x":0, "y":0, "z":0}
        # Position mode; only absolute implemented
        self.position_mode = "absolute"

        # Nozzle diameter in mm
        self.nozzle_size = nozzle_size
        # Filament diameter in mm
        self.filament_diameter = filament_diameter
        # Layer height in mm
        self.layer_height = layer_height
        # Line width in mm
        self.line_width = line_width

        # Extruder temp
        self.extruder_temp = extruder_temp
        # Bed temp
        self.bed_temp = bed_temp

        ## Defaults

        # Feed rate in mm/min
        self.feed_rate = 100

    ## Properties

    @property
    def filament_diameter(self):
        return self._filament_diameter

    @filament_diameter.setter
    def filament_diameter(self, diameter):
        if not diameter > 0.00:
            raise ValueError("Filament diameter must be > 0.00!")
        self._filament_diameter = diameter

    @property
    def nozzle_size(self):
        return self._nozzle_size

    @nozzle_size.setter
    def nozzle_size(self, diameter):
        if not diameter > 0.00:
            raise ValueError("Nozzle size must be > 0.00!")
        self._nozzle_size = diameter

    @property
    def feed_rate(self):
        return self._feed_rate

    @feed_rate.setter
    def feed_rate(self, rate):
        #TODO: Check for min/max?
        self._feed_rate = rate

    @property
    def extruder_temp(self):
        return self._extruder_temp

    @extruder_temp.setter
    def extruder_temp(self, temp):
        if temp < 180 or temp > 280:
            raise ValueError("Extruder temp {} must be between 180C and 280C".format(temp))
        else:
            self._extruder_temp = temp

    @property
    def bed_temp(self):
        return self._bed_temp

    @bed_temp.setter
    def bed_temp(self, temp):
        if temp > 0 and temp < 50 or temp > 120:
            raise ValueError("bed temp {} must be between 50C and 120C".format(temp))
        else:
            self._bed_temp = temp

    @property
    def layer_height(self):
        return self._layer_height

    @layer_height.setter
    def layer_height(self, height):
        # Check for 0.8 max height/nozzle ratio
        if height / self.nozzle_size > 0.8:
            raise ValueError("Layer height / nozzle size ratio of {} is > 0.8".format(height /
                self.nozzle_size))
        self._layer_height = height

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, width):
        # Set to 1.2 width/nozzle ratio if unset
        if width == None:
            self._line_width = self.nozzle_size * 1.2
        # Check for 1.2 min
        elif width / self.nozzle_size < 1.2:
            raise ValueError("Line width / nozzle size ratio of {} must be > 1.2".format(width / self.nozzle_size))
        # Value is good
        else:
            self._line_width = width

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, coord):
        if not {"x", "y", "z"} <= set(coord):
            raise ValueError("Position requires {x,y,z} dict")
        else:
            self._position = coord

    ## Methods

    def distance(self, x, y):
        "Get pythagorean distance for offsets"

        if x == 0:
            return y
        elif y == 0:
            return x
        else:
            return sqrt(x**2 + y**2)

    def extrusion(self, distance):
        "Get filament distance for move distance"

        # Store values
        n = self.nozzle_size
        h = self.layer_height
        r = h / 2
        w = self.line_width

        # Calculate capsule cross-section of filament
        #   See http://manual.slic3r.org/advanced/flow-math
        area = (w - h)*h + pi*(r)**2

        # Multiply by distance
        return area * distance

    def move(self, x=None, y=None, z=None, extrude=True, comment=None):
        "Generate gcode for moving in a straight line and/or extruding"

        # Command output arguments
        kwargs = {}

        # Wrap to initialize rate storage
        try:
            # Output feed rate if it changed
            if self._prev_rate != self.feed_rate:
                kwargs["f"] = self.feed_rate
        # Output if it wasn't defined, too
        except AttributeError:
            kwargs["f"] = self.feed_rate
        finally:
            # Store feed rate
            self._prev_rate = self.feed_rate

        # Check inputs
        if x == None:
            x = self.position["x"]
        else:
            kwargs["x"] = x
        if y == None:
            y = self.position["y"]
        else:
            kwargs["y"] = y
        if z == None:
            z = self.position["z"]
        else:
            kwargs["z"] = z

        # Get offsets from current position
        x_offset = abs(x - self.position["x"])
        y_offset = abs(y - self.position["y"])
        z_offset = abs(z - self.position["z"])

        # Update to new position
        self.position = {"x": x_offset, "y": y_offset, "z": z_offset}

        # Get movement distance
        distance = self.distance(x_offset, y_offset)

        # Get extrusion distance if requested
        if extrude:
            extrusion = self.extrusion(distance)
            kwargs["e"] = extrusion

        self.write("G1", comment=comment, **kwargs)

    def preamble(self):
        """
        Write out preamble commands

        This preamble is for the Original Prusa i3 Mk2
        """

        # Set units to millimeters
        self.write("G21", "millimeter units")
        # Set absolute positioning
        self.write("G90", "absolute positioning")
        # Set relative extrusion
        self.write("M83", "relative extrusion")
        # Home axes without MBL
        self.write("G28", "home without leveling", w="")

        # Start extruder temp
        self.write("M104", "start heating extruder", s=self.extruder_temp)
        # Start bed temp if enabled
        if self.bed_temp > 0:
            self.write("M140", "start heating bed", s=self.bed_temp)

        # Perform MBL
        self.write("M80", "perform mesh bed leveling")

        # Store position; z = 0.15 after leveling
        self.position = {"x": 0, "y": 0, "z": 0.15}

        # Wait on bed temp if enabled
        if self.bed_temp > 0:
            self.write("M190", "wait for bed temp", s=self.bed_temp)
        # Wait on extruder temp
        self.write("M109", "wait for extruder temp", s=self.extruder_temp)

        # Go outside print area
        self.feed_rate = 1000
        self.move(y=-3.0, comment="move outside print area", extrude=False)

        # Store line width
        line_width = self.line_width

        # Print thick intro line
        self.line_width = 0.8
        self.move(x=60, comment="print first wipe line")

        # Print thicker intro line
        self.line_width = 1.6
        self.move(x=100, comment="print second wipe line")

        # Restore line width
        self.line_width = line_width

    def write(self, code, comment=None, **kwargs):
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

        if comment:
            command += " ; {}".format(comment)

        # Print to stdout
        print(command)


# Entry point
if __name__ == "__main__":
    try:
        gcode = GCode(
            nozzle_size=0.4,
            layer_height=0.2,
            extruder_temp=200,
            bed_temp=60
        )
        gcode.preamble()
        gcode.move(z=20, extrude=False)
    except ValueError as e:
        print("Incorrect value: {}".format(e))
#    except Exception as e:
#        print("Exception: {}".format(e))
#        raise e
