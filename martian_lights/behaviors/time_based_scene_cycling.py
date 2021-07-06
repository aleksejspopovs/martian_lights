from martian_lights.helpers.schema import action_put, condition, virtual_sensor

def time_based_scene_cycling(
	ml,
	switch_sensor_id,
	group_id,
	scenes,
	on_event=None,
	off_event=None,
	cycle_event=None,
	display_name='Timed scenes'
):
	"""
	A behavior that makes the switch turn the group on to a scene that is picked
	based on the current time. It can also handle turning the group off or cycling
	through the scenes when it is on.

	off_event and cycling_event cannot be the same, but any one of them can be the
	same as on_event.

	scenes is a list of tuples of the form (time_range, scene_id), e.g.
	`('T17:00:00/T20:00:00', 'GhRn89mSmwR2f-m')`.

	This is conceptually similar to the time-based behavior available in the
	official Hue app for the latest generation of the Hue Dimmer, although the
	actual implementation is simplified somewhat.
	"""
	# the state machine is:
	# - 0: everything is off
	# - 1: things are being turned on, need to find the correct scene
	# - (1 + x): things are turned on to scene x
	cycling_state_id = ml.resource(
		'sensors',
		'cycling_state',
		virtual_sensor(f'{display_name} state')
	)

	cycling_state_addr = f'/sensors/{cycling_state_id}/state'
	cycling_state_status_addr = f'{cycling_state_addr}/status'

	event_addr = f'/sensors/{switch_sensor_id}/state/buttonevent'
	lastupdated_addr = f'/sensors/{switch_sensor_id}/state/lastupdated'
	any_on_addr = f'/groups/{group_id}/state/any_on'
	group_action_addr = f'/groups/{group_id}/action'

	if on_event is not None:
		ml.resource(
			'rules',
			'on',
			{
				'name': f'{display_name} on',
				'conditions': [
					condition(event_addr, 'eq', on_event),
					condition(lastupdated_addr, 'dx'),
					condition(any_on_addr, 'eq', 'false')
				],
				'actions': [action_put(cycling_state_addr, {'status': 1})]
			}
		)

	if off_event is not None:
		ml.resource(
			'rules',
			'off',
			{
				'name': f'{display_name} off',
				'conditions': [
					condition(event_addr, 'eq', off_event),
					condition(lastupdated_addr, 'dx'),
					condition(any_on_addr, 'eq', 'true')
				],
				'actions': [
					action_put(cycling_state_addr, {'status': 0}),
					action_put(group_action_addr, {'on': False, 'transitiontime': 4}),
				]
			}
		)

	if cycle_event is not None:
		for i in range(len(scenes)):
			ml.resource(
				'rules',
				f'advance_{i}',
				{
					'name': f'{display_name} advance {i}',
					'conditions': [
						condition(event_addr, 'eq', cycle_event),
						condition(lastupdated_addr, 'dx'),
						condition(cycling_state_status_addr ,'eq', str(2 + i))
					],
					'actions': [
						action_put(cycling_state_addr, {'status': 2 + (i + 1) % len(scenes)})
					]
				}
			)

	for i, (time_range, scene_id) in enumerate(scenes):
		ml.resource(
			'rules',
			f'init_{i}',
			{
				'name': f'{display_name} init {i}',
				'conditions': [
					condition(cycling_state_status_addr, 'eq', '1'),
					condition(cycling_state_status_addr, 'dx'),
					condition('/config/localtime', 'in', time_range),
				],
				'actions': [action_put(cycling_state_addr, {'status': 2 + i})]
			}
		)

		ml.resource(
			'rules',
			f'set_{i}',
			{
				'name': f'{display_name} set {i}',
				'conditions': [
					condition(cycling_state_status_addr, 'eq', str(2 + i)),
					condition(cycling_state_status_addr, 'dx')
				],
				'actions': [action_put(group_action_addr, {
					'scene': scene_id,
				})]
			}
		)
