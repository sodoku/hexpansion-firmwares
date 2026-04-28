import asyncio
from events.input import Button, BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
from machine import Pin
import app

BUTTONS = {
	"UP": Button("UP", "SegaController", BUTTON_TYPES["UP"]),
	"DOWN": Button("DOWN", "SegaController", BUTTON_TYPES["DOWN"]),
	"LEFT": Button("LEFT", "SegaController", BUTTON_TYPES["LEFT"]),
	"RIGHT": Button("RIGHT", "SegaController", BUTTON_TYPES["RIGHT"]),
	"A": Button("A", "SegaController"),
	"B": Button("B", "SegaController", BUTTON_TYPES["CANCEL"]),
	"C": Button("C", "SegaController"),
	"X": Button("D", "SegaController"),
	"Y": Button("E", "SegaController"),
	"Z": Button("F", "SegaController"),
	"START": Button("START", "SegaController", BUTTON_TYPES["CONFIRM"]),
	"MODE": Button("MODE", "SegaController"),
}

class Sega(app.App):
	def __init__(self, config=None):
		self.config = config
		self.config.pin[1].init(Pin.OUT)

	def update(self, delta=None):
		self.minimise()

	async def background_task(self):
		self.bs = bs = {}
		c=0
		tb=True
		while 1:
			last_states = {b: v for (b, v) in bs.items()}
			c+=1
			for i, state in enumerate([1, 0] * 8):
				self.config.pin[1].value(state)
				if i == 2:
					ls=[not self.config.ls_pin[x].value() for x in range(5)]
					bs['UP'] = ls[0]
					bs['DOWN'] = ls[1]
					bs['LEFT'] = ls[2]
					bs['RIGHT'] = ls[3]
					bs['B'] = ls[4]
					bs['C'] = not self.config.pin[0].value()
				if i == 3:
					bs['A'] = not self.config.ls_pin[4].value()
					bs['START'] = not self.config.pin[0].value()
				if c>20 and i==7:
					ls = [self.config.ls_pin[x].value() for x in range(4)]
					tb = ls[0] and ls[1] and not ls[2] and not ls[3]
					c = 0
					break
				if not tb and i == 8:
					ls=[not self.config.ls_pin[x].value() for x in range(4)]
					bs['Z'] = ls[0]
					bs['Y'] = ls[1]
					bs['X'] = ls[2]
					bs['MODE'] = ls[3]
			self.config.pin[1].value(1)

			if all(bs.values()):
				await asyncio.sleep(5)
				continue

			for button, value in bs.items():
				if value and not last_states.get(button):
					await eventbus.emit_async(ButtonDownEvent(button=BUTTONS[button]))
				if not value and last_states.get(button):
					await eventbus.emit_async(ButtonUpEvent(button=BUTTONS[button]))

			await asyncio.sleep(0.05)

__app_export__ = Sega
