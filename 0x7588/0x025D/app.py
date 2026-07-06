from app import App
import asyncio
import machine
from tildagonos import tildagonos
import vfs

INSERTED = 0
REMOVED = 1

class DualSdApp(App):
    def __init__(self, config):
        self._card_detect_slot_1 = config.ls_pin[0]
        self._card_detect_slot_1.init(self._card_detect_slot_1.IN)

        self._card_detect_slot_2 = config.ls_pin[3]
        self._card_detect_slot_2.init(self._card_detect_slot_2.IN)

        self._hex_config = config

    async def background_task(self):
        slot_1_state = REMOVED
        slot_2_state = REMOVED
        
        while True:
            await asyncio.sleep(1)

            slot_1_state_now = self._card_detect_slot_1.value()
            slot_2_state_now = self._card_detect_slot_2.value()

            if slot_1_state != slot_1_state_now:
                slot_1_state = slot_1_state_now
                if slot_1_state == INSERTED:
                    self._on_card_1_inserted()
                elif slot_1_state == REMOVED:
                    self._on_card_1_removed()

            if slot_2_state != slot_2_state_now:
                slot_2_state = slot_2_state_now
                if slot_2_state == INSERTED:
                    self._on_card_2_inserted()
                elif slot_2_state == REMOVED:
                    self._on_card_2_removed()

    def _on_card_1_inserted(self):
        print("Card 1 inserted")

        card_1 = machine.SDCard(
            slot = 3,
            width = 1,
            sck = self._hex_config.pin[2],
            miso = self._hex_config.pin[3],
            mosi = self._hex_config.pin[1],
            cs = self._hex_config.pin[0],
        )

        vfs.mount(card_1, "/sdcard_1")

    def _on_card_1_removed(self):
        print("Card 1 removed")
        vfs.umount("/sdcard_1")
        
    def _on_card_2_inserted(self):
        print("Card 2 inserted")
         
    def _on_card_2_removed(self):
        print("Card 2 removed")

__app_export__ = DualSdApp
