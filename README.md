# Martian Lights

Martian Lights (ML) is a tool for declaratively configuring a Philips Hue Bridge. You write Python code that constructs a set of resources (groups, scenes, rules, schedules, and so on) that you want to exist in the Bridge, and ML takes care of creating them and keeping them up to date. Users of Terraform should feel right at home.

ML uses the [Hue Bridge API](https://developers.meethue.com/), but it is not developed or endorsed by Philips or Signify Holding.

# Installing ML

`pip install .` should work to put `martian_lights` into your `PATH`.

# Writing a config

An ML config is just a Python script. Every ML config needs to declare a function called `run`, and it may also declare the following strings:

- `state_path`: the path to a file where ML's state will be stored,
- `bridge_addr`: the IP address or host name for your Bridge,
- `bridge_username`: the username for your bridge (if you don't have one, follow [these instructions](https://developers.meethue.com/develop/get-started-2/)).

These can also be set with the environment variables `HUE_STATE_PATH`, `HUE_BRIDGE_ADDR`, and `HUE_BRIDGE_USERNAME`.

The `run` function is where the fun happens. It takes a single parameter (say, `ml`) of type `MartianLights`, which exposes the function `resource(kind, name, attributes)`. You can call `ml.resource` to tell ML that you would like a resource of a given kind to exist with the given parameters. The name is not sent to the Bridge, it is only used to persist the created resource's ID in the statefile.

A simple config file might look like this:

```python
state_path = 'state.json'

def run(ml):
	group_id = ml.resource('groups', 'my_basement_group', {
		'name': 'Basement',
		'lights': ['1', '2'],
	})
```

Create an empty state file it can use and run ML:

```
$ echo "{}" > state.json
$ martian_lights test.py
[INFO] groups.my_basement_group: Refreshing.
[INFO] groups.my_basement_group: Creating.
[INFO] groups.my_basement_group: Created with ID 4.
[INFO] Checking for ghost resources.
[INFO] Updating local state.
```

There you go, ML has created your group for you! Note that the ID for the group you created is available to you in the `group_id` variable, so you can now refer to it in other resources that you create, like rules or scenes.

If you run ML again, nothing will happen, because the group already exists. ML knows that because it stores the association between the name `my_basement_group` and the ID 4 in the state file:

```
$ martian_lights test.py
[INFO] groups.my_basement_group: Refreshing.
[INFO] groups.my_basement_group: Found ID in state: 4
[INFO] groups.my_basement_group: Resource is up to date, no action needed.
[INFO] Checking for ghost resources.
[INFO] Updating local state.
```

If you find a spare bulb and decide to add it to the group, just change the `'lights'` parameter in your config and ML will pick up the change:

```
$ martian_lights test.py
[INFO] groups.my_basement_group: Refreshing.
[INFO] groups.my_basement_group: Found ID in state: 4
[INFO] groups.my_basement_group: Attributes ['lights'] are incorrect, updating.
[INFO] groups.my_basement_group: Updated.
[INFO] Checking for ghost resources.
[INFO] Updating local state.
```

# Advanced usage

`ml.namespace('foo')` will return a proxy object that behaves just like `ml`, but prefixes all resource names with `foo`, so `ml.namespace('foo').resource('rules', 'bar', ...)` will create a rule that is called `foo/bar` in the state file. This allows you to write modular code that can call resources whatever it wants without worrying about some other part of the code using the same name.

The module `martian_lights.helpers` contains some functionality that might be helpful when defining your resources, while `martian_lights.behaviors` contains ready-made sets of Bridge rules for complex behaviors, like making a rotary switch adjust the brightness of your lights or cycling through scenes.

[`home.py`](./home.py) is the config I use in my own apartment.
