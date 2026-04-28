import app


class InfraRed(app.App):
	def __init__(self, config=None):
		self.config = config

	def update(self, delta=None):
		self.minimise()


__app_export__ = InfraRed
