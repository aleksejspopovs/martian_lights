from martian_lights.helpers.schema import action_put, condition

def zll_switch_brightness(
	ml,
	switch,
	group_id,
	display_name='Brightness'
):
	"""
	A behavior that makes buttons on the given switch adjust the brightness of
	the given group.

	Based on the official Hue app's rules for the Hue Dimmer.
	"""
	group_action_addr = f'/groups/{group_id}/action'

	for name, conditions, bri_inc, delay in [
		('slow_up', switch.dim_up().initial_press(), 51, 10),
		('fast_up', switch.dim_up().hold(), 51, 10),
		('stop_up', switch.dim_up().long_release(), 0, 4),
		('slow_down', switch.dim_down().initial_press(), -51, 10),
		('fast_down', switch.dim_down().hold(), -51, 10),
		('stop_down', switch.dim_down().long_release(), 0, 4),
	]:
		ml.resource(
			'rules',
			name,
			{
				'name': f'{display_name} {name}',
				'status': 'enabled',
				'recycle': False,
				'conditions': conditions,
				'actions': [action_put(
					group_action_addr,
					{'transitiontime': delay, 'bri_inc': bri_inc},
				)],
			}
		)
