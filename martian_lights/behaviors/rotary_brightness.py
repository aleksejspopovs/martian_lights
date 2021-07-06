from martian_lights.helpers.schema import action_put, condition

def rotary_brightness(
	ml,
	rotary_sensor_id,
	group_id,
	slow_rotation_turns_lights_to=4,
	fast_rotation_turns_lights_to=127,
	display_name='Rotary'
):
	"""
	A behavior that makes the given rotary sensor adjust the brightness
	of the given group.

	If the group is off, rotating in either direction will set its
	brightness to `slow_rotation_turns_lights_to` or `fast_rotation_turns_lights_to`.
	If both are set to None, rotation will not turn the group on.

	Based on the official Hue app's rules for the Lutron Aurora.
	"""

	rot_addr = f'/sensors/{rotary_sensor_id}/state/expectedrotation'
	lastupdated_addr = f'/sensors/{rotary_sensor_id}/state/lastupdated'
	any_on_addr = f'/groups/{group_id}/state/any_on'
	action_addr = f'/groups/{group_id}/action'

	def make_adjustment_rule(i, rot_min, rot_max, bri_inc, transition):
		conditions = [
			condition(lastupdated_addr, 'dx'),
			condition(any_on_addr, 'eq', 'true'),
		]

		if rot_min is not None:
			conditions.append(condition(rot_addr, 'gt', rot_min))

		if rot_max is not None:
			conditions.append(condition(rot_addr, 'lt', rot_max))

		return ml.resource(
			'rules',
			f'rotation_{i}',
			{
				'name': f'{display_name} Adj {i}',
				'status': 'enabled',
				'recycle': False,
				'conditions': conditions,
				'actions': [action_put(action_addr, {
					'bri_inc': bri_inc,
					'transitiontime': transition,
				})],
			}
		)

	def make_rule_for_turning_lights_on(i, operator, value, bri, transition):
		return ml.resource(
			'rules',
			f'on_{i}',
			{
				'name': f'{display_name} On {i}',
				'status': 'enabled',
				'recycle': False,
				'conditions': [
					condition(rot_addr, operator, value),
					condition(lastupdated_addr, 'dx'),
					condition(any_on_addr, 'eq', 'false'),
				],
				'actions': [action_put(action_addr, {
					'on': True,
					'bri': bri,
					'transitiontime': transition,
				})],
			}
		)

	consts = [
		('1', '19', 6, 4),
		('-20', '-2', -6, 4),
		('18', '38', 13, 4),
		('-39', '-19', -13, 4),
		('37', '86', 27, 4),
		('-87', '-38', -27, 4),
		('85', '194', 57, 4),
		('-195', '-86', -57, 4),
		('193', '425', 121, 3),
		('-426', '-194', -121, 3),
		('424', None, 254, 2),
		(None, '-425', -254, 2)
	]
	for i, c in enumerate(consts):
		make_adjustment_rule(i, *c)

	if slow_rotation_turns_lights_to is not None:
		make_rule_for_turning_lights_on('slow', 'lt', '127', slow_rotation_turns_lights_to, 4)

	if fast_rotation_turns_lights_to is not None:
		make_rule_for_turning_lights_on('fast', 'gt', '126', fast_rotation_turns_lights_to, 4)
