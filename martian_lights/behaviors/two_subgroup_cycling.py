from martian_lights.helpers.schema import action_put, condition, virtual_sensor

def two_subgroup_cycling(
	ml,
	subgroups,
	advance_conditions,
	display_name='Subgroups'
):
	"""
	A behavior that makes a button cycle through two subgroups in a room.
	"""
	sg_a, sg_b = subgroups
	sg_a_any = lambda v: condition(f'/groups/{sg_a}/state/any_on', 'eq', 'true' if v else 'false')
	sg_b_any = lambda v: condition(f'/groups/{sg_b}/state/any_on', 'eq', 'true' if v else 'false')
	sg_a_set = lambda v: action_put(f'/groups/{sg_a}/action', {'on': v})
	sg_b_set = lambda v: action_put(f'/groups/{sg_b}/action', {'on': v})

	for i, conditions in enumerate(advance_conditions):
		ml.resource(
			'rules',
			f'advance_{i}_11_10',
			{
				'name': f'{display_name} advance 11->10',
				'status': 'enabled',
				'recycle': False,
				'conditions': conditions + [sg_a_any(True), sg_b_any(True)],
				'actions': [sg_b_set(False)],
			}
		)

		ml.resource(
			'rules',
			f'advance_{i}_10_01',
			{
				'name': f'{display_name} advance 10->01',
				'status': 'enabled',
				'recycle': False,
				'conditions': conditions + [sg_a_any(True), sg_b_any(False)],
				'actions': [sg_a_set(False), sg_b_set(True)],
			}
		)

		ml.resource(
			'rules',
			f'advance_{i}_01_11',
			{
				'name': f'{display_name} advance 01->11',
				'status': 'enabled',
				'recycle': False,
				'conditions': conditions + [sg_a_any(False), sg_b_any(True)],
				'actions': [sg_a_set(True), sg_b_set(True)],
			}
		)
