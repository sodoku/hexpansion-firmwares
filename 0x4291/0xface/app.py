import app
import neopixel
import asyncio
from events.input import BUTTON_TYPES, ButtonDownEvent
from system.eventbus import eventbus
from app_components import clear_background


PATH = __file__.rsplit("/", 1)[0]

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = int(v * (1.0 - s) * 255)
    q = int(v * (1.0 - s * f) * 255)
    t = int(v * (1.0 - s * (1.0 - f)) * 255)
    v = int(v * 255)
    i %= 6
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)

class Monster(app.App):
	CAPABILITIES = ['neopixels', 'grouped_neopixels', 'leds_running']

	LED_GROUPS = {
		"both": ( (0, 1), ),
		"individual": ( (0, ), (1, ), ),
	}

	def __init__(self, config=None):
		self.config = config
		self.did_change = True
		if config:
			self.inner_leds = neopixel.NeoPixel(config.pin[3], 2)	# grouped_neopixels capability
			self.setup_led_group('both')
			self.leds_running = True
		self.alignment = 0
		self.highlighted = 3
		self.color = 0, 0, 0
		self.saturation = 1
		self.segments = 12
		eventbus.on_async(ButtonDownEvent, self._button_handler, self)

	# grouped_neopixels capability
	def setup_led_group(self, led_group_name):
		self.leds = neopixel.MergedNeoPixel(self.inner_leds, self.LED_GROUPS[led_group_name])
	# End grouped_neopixels capability

	def draw(self, ctx):
		ctx.save()
		clear_background(ctx)
		ctx.line_width = 20
		segment_radians = 2*3.1415 / self.segments
		ctx.rotate(-3 * segment_radians)
		for i in range(self.segments):
			color = hsv_to_rgb(1.0/self.segments * i, self.saturation, 1)
			ctx.rgb(*color).arc(0, 0, 100, i*segment_radians, (i+1)*segment_radians, 0).stroke()
			if i == self.highlighted:
				ctx.save()
				ctx.rotate(-(i-2.5)*segment_radians)
				ctx.move_to(0, 80).line_to(10, 60).line_to(-10, 60).line_to(0, 80).rgb(255,255,255).fill()
				ctx.restore()
				self.color = color
		ctx.restore()

	async def _button_handler(self, event):
		if BUTTON_TYPES['UP'] in event.button:
			self.highlighted -= 1
		elif BUTTON_TYPES['DOWN'] in event.button:
			self.highlighted += 1
		elif BUTTON_TYPES['LEFT'] in event.button:
			self.saturation -= 0.1
			if self.saturation <= 0:
				self.saturation = 0
		elif BUTTON_TYPES['RIGHT'] in event.button:
			self.saturation += 0.1
			if self.saturation >= 1:
				self.saturation = 1
		elif BUTTON_TYPES['CANCEL'] in event.button:
			self.minimise()
		self.did_change = True
		self.highlighted %= self.segments

	def update(self, delta=None):
		return

	async def background_task(self):
		while True:
			if self.leds_running:
				self.leds[0] = self.color[0]//5, self.color[1]//5, self.color[2]//5
				self.leds.write()
				await asyncio.sleep(1)
			else:
				await asyncio.sleep(1)

__app_export__ = Monster
