from __future__ import print_function
from math import pi

import utils
from constants import *


class Printer(object):
    "Printer model"

    def __init__(
            self,
            bed_x=100, # mm
            bed_y=100, # mm
            nozzle_size=0.4, # mm
            filament_diameter=1.75, # mm
            extrusion_multiplier=1.0,
            retract_distance=1.0, # mm
            retract_speed=30, # mm/s
            layer_height=0.2, # mm
            line_width=None, # mm, None = auto
            extruder_temp=190, # C
            bed_temp=0 # C
        ):
        # XYZ position matrix
        self.position = {"x":0, "y":0, "z":0}
        # Position mode; only absolute implemented
        self.position_mode = "absolute"

        # Bed X size in mm
        self.bed_x = bed_x
        # Bed Y size in mm
        self.bed_y = bed_y

        # Nozzle diameter in mm
        self.nozzle_size = nozzle_size
        # Filament diameter in mm
        self.filament_diameter = filament_diameter
        # Extrusion multiplier
        self.extrusion_multiplier = extrusion_multiplier
        # Retraction distance
        self.retract_distance = retract_distance
        # Retraction speed
        self.retract_speed = retract_speed

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
        self.feed_rate = utils.mms_to_mmm(20)

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
    def extrusion_multiplier(self):
        return self._extrusion_multiplier

    @extrusion_multiplier.setter
    def extrusion_multiplier(self, multiplier):
        self._extrusion_multiplier = multiplier

    @property
    def retract_distance(self):
        return self._retract_distance

    @retract_distance.setter
    def retract_distance(self, distance):
        self._retract_distance = distance

    @property
    def retract_speed(self):
        return self._retract_speed

    @retract_speed.setter
    def retract_speed(self, speed):
        self._retract_speed = speed

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

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, unit_type):
        if unit_type == Units.mm:
            utils.write("G21", comment="millimeter units")
        else:
            raise ValueError("Only mm units implemented")
        self._units = unit_type

    @property
    def positioning(self):
        return self._positioning

    @positioning.setter
    def positioning(self, mode):
        if mode == Offsets.absolute:
            utils.write("G90", comment="absolute positioning")
        elif mode == Offsets.relative:
            raise ValueError("Relative positioning not implemented")
            #utils.write("G91", comment="relative positioning")
        self._positioning = mode

    @property
    def extruding(self):
        return self._extruding

    @extruding.setter
    def extruding(self, mode):
        if mode == Offsets.absolute:
            raise ValueError("Absolute extruding not implemented")
            #utils.write("M82", comment="absolute extruding")
        elif mode == Offsets.relative:
            utils.write("M83", comment="relative extruding")
        self._extruding = mode

    @property
    def fan(self):
        return self._fan_speed

    @fan.setter
    def fan(self, speed):
        if speed == 0:
            utils.write("M107", comment="turn off fan")
        else:
            utils.write("M106", comment="turn on fan", s=int(speed/100.0*255))
        self._fan_speed = speed

    ## Methods

    def level_mk2(self):
        "Perform bed leveling"

        utils.write("G80", comment="perform mesh bed-leveling")

        # Store position; z = 0.15 after leveling
        self.position = {"x": 0, "y": 0, "z": 0.15}

    def home(self, axes=("x", "y", "z"), comment=None):
        "Home a set of axes"

        utils.write("G28", *axes, comment=comment)

    def idle(self):
        "Disable motor idle hold"

        utils.write("M84", comment="disable motor idle hold")

    def heat(self, extruder_temp=None, bed_temp=None, wait=False):
        "Heat up components, optionally waiting"

        def extruder(temp):
            # Use configured temp if none supplied
            if temp == None:
                temp = self.extruder_temp

            if temp == 0:
                action="M104"
                comment="turn off extruder"
            elif wait:
                action="M109"
                comment="wait for extruder temp"
            else:
                action="M104"
                comment="start heating extruder"
                
            utils.write(action, comment=comment, s=temp)
                
        def bed(temp):
            # Use configured temp if none supplied
            if temp == None:
                temp = self.bed_temp

            if temp == 0:
                action="M140"
                comment="turn off bed"
            elif wait:
                action="M190"
                comment="wait for bed temp"
            else:
                action="M140"
                comment="start heating bed"
                
            utils.write(action, comment=comment, s=temp)

        # Heat and continue
        if not wait:
            extruder(extruder_temp)
            bed(bed_temp)
        # Wait for temps
        else:
            bed(bed_temp)
            extruder(extruder_temp)

    def move(self, x=None, y=None, z=None, extrude=Extrusion.extrude, rate=None, comment=None):
        "Generate gcode for moving in a straight line and/or extruding"

        # Generate retraction if requested
        if extrude == Extrusion.retract or extrude == Extrusion.retract_only:
            utils.write("G1", comment="retract", e=-self.retract_distance,
		f=utils.mms_to_mmm(self.retract_speed))
            self._prev_rate = utils.mms_to_mmm(self.retract_speed)

        # Set feed rate
        if rate:
            self.feed_rate = utils.mms_to_mmm(rate)

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
        elif x != self.position["x"]:
            kwargs["x"] = x
        if y == None:
            y = self.position["y"]
        elif y != self.position["y"]:
            kwargs["y"] = y
        if z == None:
            z = self.position["z"]
        elif z != self.position["z"]:
            kwargs["z"] = z

        # Get offsets from current position
        x_offset = abs(x - self.position["x"])
        y_offset = abs(y - self.position["y"])
        z_offset = abs(z - self.position["z"])

        # Update to new position
        self.position = {"x": x, "y": y, "z": z}

        # Get movement distance
        distance = utils.distance(x_offset, y_offset)

        # Get extrusion distance if requested
        if extrude == Extrusion.extrude:
            extrusion = self.extrusion(distance)
            kwargs["e"] = extrusion

        # Write out move command
        utils.write("G1", comment=comment, **kwargs)

        # Advance if we retracted before
        if extrude == Extrusion.retract or extrude == Extrusion.advance_only:
            utils.write("G1", comment="advance", e=self.retract_distance,
		f=utils.mms_to_mmm(self.retract_speed))
            self._prev_rate = utils.mms_to_mmm(self.retract_speed)

    def hop(self, x=None, y=None, height=0.1, comment=None, rate=None):
        "Z-hop height above current Z, move to X/Y, then drop back down"

        # Store current Z
        z = self.position["z"]

        # Hop
        self.move(z=z + height, comment="Z hop", extrude=Extrusion.retract_only, rate=100)
        # Move
        self.move(x, y, comment=comment, extrude=Extrusion.idle, rate=rate)
        # Drop
        self.move(z=z, comment="Z drop", extrude=Extrusion.advance_only, rate=100)

    def rect(self, x1, y1, x2, y2, rate=None):
        """
        Move to x1,y1, then draw a rectangle of single lines
        Move back to 0,0 at end if home=True
        Retract before start and end if retract=True
        """

        # Set rate if provided
        if rate:
            self.feed_rate = utils.mms_to_mmm(rate)

        # Draw rectangle lines
        self.move(x2, y1, comment="lower right")
        self.move(x2, y2, comment="upper right")
        self.move(x1, y2, comment="upper left")
        self.move(x1, y1, comment="lower left")

    def extrusion(self, distance):
	"Get filament distance for move distance"

	# Store values
	f = self.filament_diameter
	fr = f / 2
	e = self.extrusion_multiplier
	n = self.nozzle_size
	h = self.layer_height
	hr = h / 2
	w = self.line_width

	# Calculate capsule cross-section of filament
	#   See http://manual.slic3r.org/advanced/flow-math
	area = (w - h)*h + pi*(hr)**2

	# Volume of line
	volume = area * distance

	# Filament length, scaled by extrusion multiplier
	#   length mm = capsule mm^3 / filament mm^2 * multiplier
	length = volume/(pi*fr**2)*e

	# Return length for extruder
	return length

