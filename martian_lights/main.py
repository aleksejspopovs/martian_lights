import logging
import os

from martian_lights.core import MartianLights

def do_the_thing(ml):
	sensor_id = ml.resource('sensors', 'fake_sensor', {
		'name': 'fake sensor',
		'modelid': 'IMSOFAKE',
		'swversion': '1.0',
		'type': 'CLIPGenericStatus',
		'uniqueid': 'fake-00',
		'manufacturername': 'Aleksejs'
	})

	ml.resource('sensors', 'fake_sensor_2', {
		'name': f'other sensor, after {sensor_id}',
		'modelid': 'IMSOFAKE',
		'swversion': '1.0',
		'type': 'CLIPGenericStatus',
		'uniqueid': 'fake-01',
		'manufacturername': 'Aleksejs'
	})

def main():
	logging.basicConfig(
		level=logging.INFO,
		format='[%(levelname)s] %(message)s'
	)

	ml = MartianLights('state.json', os.getenv('HUE_BRIDGE_ADDR'), os.getenv('HUE_BRIDGE_USERNAME'))
	ran_cleanly = True

	try:
		do_the_thing(ml)
	except Exception as error:
		ran_cleanly = False
		logging.error(repr(error))
	finally:
		if ran_cleanly:
			ml.delete_ghost_resources()
		ml.save_state()

if __name__ == '__main__':
	main()
