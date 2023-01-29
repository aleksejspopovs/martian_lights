from martian_lights.helpers.schema import action_put, condition, virtual_sensor

def time_based_scene_cycling(
	ml,
	group_id,
	scenes,
	on_conditions=(),
	off_conditions=(),
	toggle_conditions=(),
	cycle_conditions=(),
	extra_off_actions=(),
	display_name='Timed scenes',
):
	"""
	A behavior that makes the switch turn the group on to a scene that is picked
	based on the current time. It can also handle turning the group off or cycling
	through the scenes when it is on.

	off_conditions and cycling_conditions should be mutually exclusive, but neither
	needs to be mutually exclusive with on_conditions.

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

	any_on_addr = f'/groups/{group_id}/state/any_on'
	group_action_addr = f'/groups/{group_id}/action'

	full_on_conditions = (
		list(on_conditions)
		+ [x + [condition(any_on_addr, 'eq', 'false')] for x in toggle_conditions]
	)
	full_off_conditions = (
		list(off_conditions)
		+ [x + [condition(any_on_addr, 'eq', 'true')] for x in toggle_conditions]
	)

	for cond_i, conditions in enumerate(full_on_conditions):
		ml.resource(
			'rules',
			f'on_{cond_i}',
			{
				'name': f'{display_name} on',
				'conditions': conditions,
				'actions': [action_put(cycling_state_addr, {'status': 1})]
			}
		)

	for cond_i, conditions in enumerate(full_off_conditions):
		ml.resource(
			'rules',
			f'off_{cond_i}',
			{
				'name': f'{display_name} off',
				'conditions': conditions,
				'actions': [
					action_put(cycling_state_addr, {'status': 0}),
					action_put(group_action_addr, {'on': False}),
				] + list(extra_off_actions)
			}
		)

	for cond_i, conditions in enumerate(cycle_conditions):
		for i in range(len(scenes)):
			ml.resource(
				'rules',
				f'advance_{i}_{cond_i}',
				{
					'name': f'{display_name} advance {i}',
					'conditions': conditions + [condition(cycling_state_status_addr ,'eq', str(2 + i))],
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

	return cycling_state_id
