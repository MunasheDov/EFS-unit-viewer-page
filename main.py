import re
import tempfile
import os
import json

# Define the column names for the "stats" section
stats_columns = [
		"move_type", "kind", "move", "spot", "camo", "agility", "armor", "psy_def",
		"water_acc", "water_dmg", "indirect_acc", "indirect_dmg", "air_acc", "air_dmg", "direct_acc", "direct_dmg",
		"close_acc", "close_dmg",  "psy_acc", "psy_dmg", "ranged_sp_acc", "ranged_sp_dmg", "direct_sp_acc", "direct_sp_dmg", "close_sp_acc", "close_sp_dmg",
		"cargo", "can_b_cargo", "unit_function", "crd_trn", "cred",
		"food", "energy", "metal", "trace", "exotica", "chemicals", "biochems", "electronics",
		"ceramsteel", "wetware", "monopols", "gems", "singularities",
		"unit", "t_lvl", "bldgs", "owner", "turns_2_bld",
		"tech_0", "tech_1", "tech_2", "tech_3", "tech_4", "tech_5", "tech_6", "tech_7", "tech_8", "tech_9",
		"tax", "flock", "range", "eat", "rank", "rop", "disband",
		"art", "animation", "icon"
]


def format_combat(unit):
	sections = stats_columns[stats_columns.index("water_acc"):stats_columns.index("close_sp_dmg")+1]
	results = {}
	stats = unit["stats"]
	for i in range(0, len(sections)-1, 2):
		acc, dmg = sections[i], sections[i+1]
		if stats[acc] + stats[dmg] > 0:
			results[acc[0:len(acc)-len("_acc")]] = str(stats[acc])+'/'+str(stats[dmg])
	return results

def format_behavior(unit):
	sections = stats_columns[stats_columns.index("move"):stats_columns.index("psy_def")+1]
	results = {}
	stats = unit["stats"]
	for item in sections:
			results[item] = stats[item]
	return results

def parse_quoted_pairs(input_string):
		# Use regex to match pairs of quoted strings
		pattern = r'"([^"]+)"'
		# Find all matches and return as list of tuples
		return re.findall(pattern, input_string)

def map_keys_to_numbers(keys, number_string):
		values = number_string.split()
		for i in range(len(values)):
				values[i] = int(values[i]) if values[i].isdigit() else values[i]


		#if len(keys) != len(numbers):
		#    raise ValueError("Number of keys does not match number of values")
		return dict(zip(keys, values))

def parse_game_data(file_path):
		units = []
		base_types = []
		current_unit = {}
		last_sprite_index = 0
		base_type = False
		unit_count = 0
		with open(file_path, 'r') as file:
				for line in file:
						line = line.strip()
						if not line or line.startswith('//'):
								continue

						if line.startswith('{'):
								current_unit = {}
								last_sprite_index = int(line[1:])
								base_type = True
								continue

						if line.startswith('}'):
							continue


						current_unit["index"] = len(units)
						current_unit["sprite_index"] = last_sprite_index

						current_unit["is_base_type"] = base_type

						base_type = False
						parts = parse_quoted_pairs(line)

						current_unit["name"]   = parts[parts.index("name")+1]
						current_unit["abbrev"] = parts[parts.index("abbrev")+1]

						stats = map_keys_to_numbers(stats_columns, parts[parts.index("stats")+1])
						current_unit["stats"]  = stats

						art_idx = parts.index("art")
						current_unit["art"] = {
							"animation": parts[art_idx+1],
							"icon": parts[art_idx+2]
						}
						current_unit["sprite_name"] = last_sprite_index
						if current_unit["art"]["icon"] != "efsunit.bin" and current_unit["art"]["icon"] != "same":
							current_unit["sprite_name"] = current_unit["art"]["icon"]
						units.append(current_unit)
						if current_unit["is_base_type"]:
							base_types.append(unit_count)
						current_unit = {}
						unit_count += 1
		return units, base_types

# Test with your provided sample data
sample_data = """
{0
"name" "Grappler"               "1" "abbrev" "Grappler"    "stats" "jump            0      3      5      6     3     50      10     0   0    0   0     0   0    0   0   0   0   0   0    0   0      0   0      8 100      0         0          134217728         0       0     0       0        0       0        0         0           0           0              0          0         0        0          0          -1     -1      7       7         3        0   0   0   0   0   0   0   0   0   0    0      1       0      0      1     1       1"     "art"  "grap.flc"       "efsunit.bin"
}
{1
"name" "Blow Ship"              "1" "abbrev" "Blow Ship"   "stats" "jump            1      3      7      6     3     50      10     0   0    0   0     0   0    0   0   0   0   0   0    8 100      0   0      0   0      0         0          134217728         0       0     0       0        0       0        0         0           0           0              0          0         0        0          0          -1     -1      7       7         3        0   0   0   0   0   0   0   0   0   0    0      1       0      0      2     1       1"     "art"  "puff2.flc"      "efsunit.bin"
}
{2
"name" "Spore Ship"             "1" "abbrev" "Spore"       "stats" "jump            2      3      5      6     3     50      10     0   0    0   0     0   0    0   0   0   0   0   0    0   0      9  70      9  70      0         0          134217728         0       0     0       0        0       0        0         0           0           0              0          0         0        0          0          -1     -1      7       7         3        0   0   0   0   0   0   0   0   0   0    0      1       0      0      3     1       1"     "art"  "pdshp.flc"      "efsunit.bin"
}
"""

# # Write to a temporary file and test the parser
# with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
#     temp_file.write(sample_data)
#     temp_file_path = temp_file.name

# units = parse_game_data(temp_file_path)
# print(json.dumps(units, indent=2))

# os.unlink(temp_file_path)

enable_combat_stats = True
enable_behavior_stats = True

from pathlib import Path
unit_dat_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Emperor of the Fading Suns\DAT\UNIT.DAT')
units, base_types = parse_game_data(unit_dat_path)
#output = [ (u["name"], {"metal": u["stats"]["metal"]}) for u in units ]
8
output = []
headers = ["name"]
headers.append("art")
headers.append("turns")
headers.append("maintenance")

headers.append("Resource Costs")
if enable_combat_stats or enable_behavior_stats:
	headers.append("art")
if enable_combat_stats:
	headers.append("Weapons")
if enable_behavior_stats:
	headers.append("Stats")
#headers.append("firebirds")
#headers.extend(stats_columns[stats_columns.index("food"):stats_columns.index("singularities")+1])
headers = map(str.capitalize, headers)

for i in range(len(units)):
	units[i]["sprite_name"] = str(units[i]["sprite_name"])
	units[i]["sprite_name"] = units[i]["sprite_name"].replace(".bmp", "")

for unit in units:
	# expand truncated names
	name = unit["name"].replace("Lgn", "Legion")

	name = name.replace("Bmbr", "Bomber")
	name = name.replace("Bmber", "Bomber")

	name = name.replace("Artillery", "Art")
	name = name.replace("Art", "Artillery")

	name = name.replace("Hvy", "Heavy")

	name = name.replace("Torp", "Torpedo")

	cur = {"name": name}
	cur["index"] = unit["index"]
	cur["is_base_type"] = unit["is_base_type"]

	cur["sprite_index"] = unit["sprite_index"]
	cur["sprite_name"] = unit["sprite_name"]

	cur["turns_2_bld"] = unit["stats"]["turns_2_bld"]
	cur["crd_trn"] = unit["stats"]["crd_trn"]
	cur["costs"] = {}
	if enable_combat_stats:
		cur["combat"] = format_combat(unit)
	if enable_behavior_stats:
		cur["behavior"] = format_behavior(unit)



	if int(unit["stats"]["unit"]) > -1:
		idx_offset = 0
		if int(unit["stats"]["t_lvl"]) > -1:
			idx_offset = int(unit["stats"]["t_lvl"])
		unit_idx = int(unit["stats"]["unit"])
		cur["costs"]["unit"] = units[base_types[unit_idx]+idx_offset]["sprite_name"]



	if unit["stats"]["cred"] > 0:
		cur["costs"]["cred"] = unit["stats"]["cred"]

	total = 0
	for key in stats_columns[stats_columns.index("food"):stats_columns.index("singularities")+1]:
		if unit["stats"][key] > 0:
			cur["costs"][key] = unit["stats"][key]
		total += unit["stats"][key]
	if total > 0:
		output.append(cur)

#print(output)




from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('./templates'))

template = env.get_template('index.html')
rendered_page = template.render({"headers": headers, "units": output})

with open('index.html', 'w') as file:
	file.write(rendered_page)
print(env.loader.list_templates())
#print(json.dumps(output, indent=2))


# TODO
# - (DONE) show turn times to build
# - where a unit is build (fort, factory, farm, etc)
# - units that morph from another?
# - combat stats view
# - use fancy ingame names