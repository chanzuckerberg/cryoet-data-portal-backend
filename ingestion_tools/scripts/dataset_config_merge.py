"""
Usage (from ingestion_tools/scripts directory):
python dataset_config_merge.py (--unique-values)

Will write to OUTPUT_FILE (see below)

This file is intended to be run from the ingestion/dataset_configs directory. Intended for ensuring that all existing
dataset config files' schema are covered by the linkml/Pydantic models.
It will read all .yaml files in the directory and its subdirectories, except for the files in the whitelist.
It will then merge all of the yaml files (by their fields, retaining the nested structure) into a single yaml file.
During the merge, it attempts to retain as many fields as possible, and will print out any conflicts it encounters
(while still retaining the different types that exist in the files).
The merge is done by recursively updating the dictionary, so that nested fields are merged correctly.

Edge cases:
- If a field is a list in one file and a dict in another, the list will be kept, with the dict added to the list.
- If a field is a list in one file and a non-list in another, the list will be kept, with the non-list added to the list.
- If a field is a list in one file and a non-dict, non-list in another, the list will be kept, with the non-dict, non-list added to the list.

Some basic warnings will be printed out if there are conflicts, but the output will still be generated.
"""

import datetime
import os
from typing import Union

import click
import yaml

EXCLUDE_LIST = [
    "dataset_config_merged.yaml",
    "template.yaml",
]
EXCLUDE_KEYWORDS = ["draft"]

ALLOWED_PRIMITIVE_TYPES = [int, float, str, bool, list, datetime.date]
DATASET_CONFIGS_FOLDER = "../dataset_configs/"
OUTPUT_FILE = DATASET_CONFIGS_FOLDER + "dataset_config_merged.yaml"

keep_unique_values = False

"""
Merges two lists together, keeping only values that are of unique types (values are arbitrary, as long as they are unique).

If keep_unique_values is true, not only are unique types kept, but unique values are kept as well.
"""


def keep_unique_datatypes(original_list: list, new_value: Union[int, float, str, bool, list, datetime.date]) -> list:
    global keep_unique_values

    if new_value is None:
        return original_list

    if type(new_value) not in ALLOWED_PRIMITIVE_TYPES:
        raise ValueError(f"Invalid datatype: {new_value} | {type(new_value)}")

    if original_list is None or len(original_list) == 0:
        return [new_value]

    new_list = original_list.copy()
    if keep_unique_values and new_value not in original_list:
        new_list.append(new_value)
    elif type(new_value) not in [type(value) for value in original_list]:
        new_list.append(new_value)
        print(f"Warning: Added new datatype to list: {original_list} | {new_value}")

    return new_list


"""
Runs a data check on non-dict items and reports any warnings about potential different-type attributes across files.

If keep_unique_values is true, not only are unique types kept, but unique values are kept as well.

Returns False when there are conflicting datatypes, otherwise true.
"""


def primitive_data_check(
    original_value: Union[int, float, str, bool, list, datetime.date],
    new_value: Union[int, float, str, bool, list, datetime.date],
) -> bool:
    global keep_unique_values

    if original_value is None:
        return True

    type_original_value = type(original_value)
    type_new_value = type(new_value)

    if type_original_value not in ALLOWED_PRIMITIVE_TYPES or type_new_value not in ALLOWED_PRIMITIVE_TYPES:
        raise ValueError(f"Invalid datatype: {original_value} | {type_original_value} | {new_value} | {type_new_value}")

    if type_original_value is not type_new_value:
        print(f"Warning: Data type conflict: {original_value} | {new_value}")
        return False

    if keep_unique_values and original_value != new_value:
        return False

    return True


"""
This function is a helper function for recursive_dict_update. It is used when the new value is a list and the current value is a list.
Since we don't care about the actual values in the list (unless it's more dictionaries), and instead just the typess, we can just keep
values of unique type from the list. If it is a dictionary, we will recurse on it. If it is a list, we will just keep the list.

The function modifies / merges in-place the specified key of the current_entries dict and returns the updated current_entries dict.
current_entries[key] is modified to a list of one element if that element has dictionary descendants, otherwise the original list.
"""


def recursive_dict_update_list_helper(current_entries: dict, key: str, new_entry_values: list) -> dict:
    # nothing to update with
    if len(new_entry_values) == 0:
        return current_entries

    for i in range(len(new_entry_values)):
        # if there are nested dictionaries, recurse as neccessary
        if isinstance(new_entry_values[i], dict):
            # dictionary entry that corresponds to the new_entry_values[i] dictionary (the value that all the new_entry_values dicts are getting merged into)
            # default empty dict
            corresponding_entry: dict = {}
            # if a corresponding value alrady exists:
            if key in current_entries:
                # if it's a list, then it should have been created by this function
                # it is a list to represent the fact that it's a multivalued element (so that when the yaml gets generated, it is noted as a multivalued attribute)
                # this is only reason why it's a list: inside the list it should just have the dictionary that is new_entry_values[i]'s corresponding value
                if isinstance(current_entries[key], list):
                    assert len(current_entries[key]) == 1
                    # assign accordingly
                    corresponding_entry = current_entries[key][0]
                # if it's a dictionary, we just use it
                # note that it will never be a dictionary again, because after updating this multivalued field (we know so because we have new_entry_values as list),
                # it will become a list element with one dict element
                elif isinstance(current_entries[key], dict):
                    corresponding_entry = current_entries[key]
                else:
                    raise ValueError(
                        f"Unresolvable conflict for {current_entries[key]} (type: {type(current_entries[key])}), {new_entry_values[i]} (type: {type(new_entry_values[i])})",
                    )

            current_entries[key] = recursive_dict_update(corresponding_entry, new_entry_values[i])
        else:
            primitive_data_check(current_entries.get(key), new_entry_values)
            current_entries[key] = keep_unique_datatypes(current_entries.get(key, []), new_entry_values[i])
    # if new_entry_values was a list of dictionaries, the current_entries[key] will be a dictionary instead of a list (recursive_dict_update returns a dictionary)
    # so we need to convert it back to a list
    if not isinstance(current_entries[key], list):
        current_entries[key] = [current_entries[key]]
    return current_entries


"""
This function is the main function that will be called. It will take in the current dictionary and the new dictionary, and will merge them together. A recursive
approach is used to handle nested dictionaries and lists.

The function will return the merged dictionary, which is the current_entries dictionary.
In-place modifications are made to the current_entries dictionary, but if it is a new object, assignment of the return value is necessary.
"""


def recursive_dict_update(current_entries: dict, new_entries: dict) -> dict:
    for key, new_value in new_entries.items():
        # Regular scenarios
        if new_value is None:
            continue
        # current value: dict and new value: dict, so recurse
        if isinstance(new_value, dict) and (
            isinstance(current_entries.get(key), dict) or current_entries.get(key) is None
        ):
            current_entries[key] = recursive_dict_update(current_entries.get(key, {}), new_value)
        # current value: list and new value: list situation
        elif isinstance(new_value, list) and (
            isinstance(current_entries.get(key), list) or current_entries.get(key) is None
        ):
            current_entries = recursive_dict_update_list_helper(current_entries, key, new_value)
        # current value: dict and new value: non-dict (list or primitive)
        elif isinstance(current_entries.get(key), dict) and not isinstance(new_value, dict):
            # edge case: current value: dict and a new value: list, add the dict to the list
            if isinstance(new_value, list):
                new_list = new_value + [current_entries.get(key)]
                # and then now it is list, list situation
                current_entries = recursive_dict_update_list_helper(current_entries, key, new_list)
            # edge case: current value: dict and a new value: primitive, just keep the dict and print a warning
            else:
                print("type conflict:")
                print("Key: ", key)
                print("Current: ", current_entries.get(key))
                print("New: ", new_value)
        # current value: list and new value: non-list (dict or primitive)
        elif isinstance(current_entries.get(key), list) and not isinstance(new_value, list):
            # edge case: current value: list and new value: dict, add the dict to the list
            if isinstance(new_value, dict):
                new_list = [new_value] + current_entries.get(key)
                # and then now it is list, list situation
                current_entries = recursive_dict_update_list_helper(current_entries, key, new_list)
            # edge case: current-value: list and a new value: primitive, just keep the list and print a warning
            else:
                current_entries[key] = keep_unique_datatypes(current_entries.get(key), new_value)
        # non-dict, non-list (primitive) and non-dict, non-list (primitive)
        else:
            datatypes_match = primitive_data_check(current_entries.get(key, None), new_value)
            # if the primitive datatypes don't match, create a new list representing multiple datatypes (but not multivalued attribute necessarily)
            if not datatypes_match:
                current_entries[key] = [new_value, current_entries[key]]
            else:
                current_entries[key] = new_value

    return current_entries


@click.command()
@click.option(
    "--unique-values",
    is_flag=True,
    help="If set, not only are unique types kept, but unique values are kept as well. Note that this works only for primitive types, and non-multivalued attributes may display as multivalued (because they are represented as a list of unique values).",
)
def main(unique_values: bool):
    global keep_unique_values
    keep_unique_values = unique_values

    all_files: list[str] = [
        os.path.join(directory_path, file)
        for directory_path, _, filename in os.walk(os.path.expanduser(DATASET_CONFIGS_FOLDER))
        for file in filename
        if (file.endswith(".yaml") or file.endswith(".yml"))
        and os.path.basename(file) not in EXCLUDE_LIST
        and not any(keyword in file for keyword in EXCLUDE_KEYWORDS)
    ]

    unified_config: dict = {}

    # get all yaml files, except for the whitelist, and attempt to merge them
    for file in all_files:
        with open(file, "r") as stream:
            try:
                config_file: dict = yaml.safe_load(stream)
                # a temp is created to avoid a half-merged config file after an exception since recursive_dict_update modifies in-place
                temp_unified_config = unified_config.copy()
                recursive_dict_update(temp_unified_config, config_file)
                unified_config = temp_unified_config
            except yaml.YAMLError as exc:
                print(exc)
            except Exception:
                print("Error in file: ", file)

    # write the unified config to a new yaml file
    with open(OUTPUT_FILE, "w") as stream:
        try:
            yaml.dump(unified_config, stream)
        except yaml.YAMLError as exc:
            print(exc)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
