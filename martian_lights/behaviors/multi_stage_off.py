from martian_lights.helpers.schema import action_put, condition

def multi_stage_off(
	ml,
	condition_group_id,
	target_group_id,
	conditions,
	display_name='Global off'
):
	"""
	A behavior that makes a button turn a group off only if another group is
	already off.

	This lets you implement a multi-stage "off" button that e.g. normally
	turns off the lights in a specific room, but will also turn off all of
	the lights in the house if the room is already off.
	"""
	any_on_addr = f'/groups/{condition_group_id}/state/any_on'
	group_action_addr = f'/groups/{target_group_id}/action'

	for cond_i, cond in enumerate(conditions):
		ml.resource(
			'rules',
			f'off_{cond_i}',
			{
				'name': f'{display_name}',
				'conditions': cond + [condition(any_on_addr, 'eq', 'false')],
				'actions': [action_put(group_action_addr, {'on': False})]
			}
		)
