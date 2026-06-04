import app

class WifiResetApp(app.App):
    def __init__(self, config):
        import settings
        import power
        settings.set('wifi_ssid', 'emf')
        settings.set('wifi_wpa2ent_username', 'badge')
        settings.set('wifi_password', 'badge')
        settings.save()
        power.Off()

__app_export__ = WifiResetApp
