from martian_lights.helpers.schema import action_put, condition, virtual_sensor

def subset_cycling(
	ml,
	switch_sensor_ids,
	advance_event,
	reset_event,
	group_id,
	subsets,
	extra_on_conditions=None,
	display_name='Subsets'
):
	"""
	A behavior that makes buttons on the given switch adjust the brightness of
	the given group.

	Based on the official Hue app's rules for the Hue Dimmer.
	"""
	extra_on_conditions = extra_on_conditions or []

	sensor_addrs = [
		(f'/sensors/{x}/state/buttonevent', f'/sensors/{x}/state/lastupdated')
		for x in switch_sensor_ids
	]
	any_on_addr = f'/groups/{group_id}/state/any_on'

	# the state is exactly equal to the index of the desired subset
	cycling_state_id = ml.resource(
		'sensors',
		'cycling_state',
		virtual_sensor(f'{display_name} state')
	)

	cycling_state_addr = f'/sensors/{cycling_state_id}/state'
	cycling_state_status_addr = f'{cycling_state_addr}/status'

	all_lights = ml.read_resource('groups', group_id)['lights']
	assert all(all(x in all_lights for x in subset) for subset in subsets), \
		f'some lights in subsets {subsets} not found in group {group_id} ({all_lights})'

	for sensor_i, (event_addr, lastupdated_addr) in enumerate(sensor_addrs):
		for i in range(len(subsets)):
			next_i = (i + 1) % len(subsets)
			next_subset = subsets[next_i]
			ml.resource(
				'rules',
				f'advance_{i}_{sensor_i}',
				{
					'name': f'{display_name} advance {i}',
					'status': 'enabled',
					'recycle': False,
					'conditions': (
						[
							condition(lastupdated_addr, 'dx'),
							condition(event_addr, 'eq', advance_event),
							condition(cycling_state_status_addr, 'eq', str(i)),
							condition(any_on_addr, 'eq', 'true'),
						]
						+ extra_on_conditions
					),
					'actions': (
						[
							action_put(f'/lights/{light_id}/state', {'on': light_id in next_subset})
							for light_id in all_lights
						]
						+ [action_put(cycling_state_addr, {'status': next_i})]
					),
				}
			)

	ml.resource(
		'rules',
		'reset',
		{
			'name': f'{display_name} reset',
			'status': 'enabled',
			'recycle': False,
			'conditions': [
				condition(lastupdated_addr, 'dx'),
				condition(event_addr, 'eq', reset_event),
			],
			'actions': [action_put(cycling_state_addr, {'status': 0})],
		}
	)

	return cycling_state_id
