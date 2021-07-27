from martian_lights.helpers.schema import action_put, condition
from martian_lights.helpers.zll_switch import (
	zll_switch_event,
	ZLLSwitchButton,
	ZLLSwitchEventType,
)

def zll_switch_brightness(
	ml,
	switch_sensor_id,
	group_id,
	display_name='Brightness'
):
	"""
	A behavior that makes buttons on the given switch adjust the brightness of
	the given group.

	Based on the official Hue app's rules for the Hue Dimmer.
	"""
	event_addr = f'/sensors/{switch_sensor_id}/state/buttonevent'
	lastupdated_addr = f'/sensors/{switch_sensor_id}/state/lastupdated'
	group_action_addr = f'/groups/{group_id}/action'

	for name, button, event_type, bri_inc in [
		('slow_up', ZLLSwitchButton.DIM_UP, ZLLSwitchEventType.INITIAL_PRESS, 30),
		('fast_up', ZLLSwitchButton.DIM_UP, ZLLSwitchEventType.HOLD, 56),
		('slow_down', ZLLSwitchButton.DIM_DOWN, ZLLSwitchEventType.INITIAL_PRESS, -30),
		('fast_down', ZLLSwitchButton.DIM_DOWN, ZLLSwitchEventType.HOLD, -56),
	]:
		ml.resource(
			'rules',
			name,
			{
				'name': f'{display_name} {name}',
				'status': 'enabled',
				'recycle': False,
				'conditions': [
					condition(lastupdated_addr, 'dx'),
					condition(event_addr, 'eq', zll_switch_event(
						button,
						event_type,
					)),
				],
				'actions': [action_put(
					group_action_addr,
					{'transitiontime': 9, 'bri_inc': bri_inc},
				)],
			}
		)
