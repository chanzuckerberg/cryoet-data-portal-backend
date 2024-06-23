# TODO: add which files each attribute appears in? and what % of files it appears in?
"""
This file is intended to be run from the ingestion/dataset_configs directory. Intended for ensuring that all existing dataset config files' schema are covered by the linkml/Pydantic models.
It will read all .yaml files in the directory and its subdirectories, except for the files in the whitelist.
It will then merge all of the yaml files (by their fields, retaining the nested structure) into a single yaml file, config-field-discovery-output.yaml.
During the merge, it attempts to retain as many fields as possible, and will print out any conflicts it encounters.
The merge is done by recursively updating the dictionary, so that nested fields are merged correctly.

Edge cases:
- If a field is a list in one file and a dict in another, the list will be kept, with the dict added to the list.
- If a field is a list in one file and a non-list in another, the list will be kept, with the non-list added to the list.
- If a field is a list in one file and a non-dict, non-list in another, the list will be kept, with the non-dict, non-list added to the list.

Some basic warnings will be printed out if there are conflicts, but the output will still be generated.

Usage (from ingestion/dataset_configs):
python config-field-discovery.py
"""

import os

import yaml

EXCLUDE_LIST = [
    "./validate.yaml",
    "./config-attribute-discovery-output.yaml",
    "./template.yaml",
    "./template_draft.yaml",
]

"""
Runs a data check on non-dict items and reports any warnings about potential different-type attributes across files.

Returns False when there are conflicting datatypes, otherwise true.
"""


def raw_data_check(original_value, new_value):
    if original_value is None:
        return True

    type_original_value = type(original_value)
    type_new_value = type(new_value)

    if type_original_value is dict:
        print(f"Warning: Ran raw data check on {original_value}")

    if type_new_value is dict:
        print(f"Warning: Ran raw data check on {new_value}")

    # TODO: potential check bypasses?
    # if type_original_value in [int, float] and type_new_value in [int, float]:
    #     return True
    # if type_original_value in [int, float] and type_new_value is str and (len(new_value) == 0 or ("{" in new_value and "}" in new_value)):
    #     return True
    # if type_original_value is str and (len(original_value) == 0 or ("{" in original_value and "{" in original_value)) and type_new_value in [int, float]:
    #     return True

    if type_original_value is not type_new_value:
        print(f"Warning: Data type conflict: {original_value} | {new_value}")
        return False

    return True


"""
This function is a helper function for recursive_dict_update. It is used when the new value is a list and the current value is a list.
Since we don't care about the actual values in the list (unless it's more dictionaries), and instead just the structure, we can just keep
a single element from the new list. If it is a dictionary, we will recurse on it. If it is a list, we will just keep the list (since we don't care about the values,
but it might be insightful to have an example of the list structure).

The function returns a list of one element if that element has dictionary descendants, otherwise the original list.
"""


def recursive_dict_update_list_helper(current_entries, key, new_entries):
    # nothing to update with
    if len(new_entries) == 0:
        return current_entries

    for i in range(len(new_entries)):
        # if there are nested dictionaries, recurse as neccessary
        if isinstance(new_entries[i], dict):
            # dictionary entry that corresponds to the new_entries[i] dictionary (the value that all the new_entries dicts are getting merged into)
            # default empty dict
            corresponding_entry = {}
            # if a corresponding value alrady exists:
            if key in current_entries:
                # if it's a list, then it should have been created by this function
                # it is a list to represent the fact that it's a multivalued element (so that when the yaml gets generated, it is noted as a multivalued attribute)
                # this is only reason why it's a list: inside the list it should just have the dictionary that is new_entries[i]'s corresponding value
                if isinstance(current_entries[key], list):
                    assert len(current_entries[key]) == 1
                    # assign accordingly
                    corresponding_entry = current_entries[key][0]
                # if it's a dictionary, we just use it
                # note that it will never be a dictionary again, because after updating this multivalued field (we know so because we have new_entries as list),
                # it will become a list element with one dict element
                elif isinstance(current_entries[key], dict):
                    corresponding_entry = current_entries[key]
                else:
                    raise ValueError(
                        f"Unresolvable conflict for {current_entries[key]} (type: {type(current_entries[key])}), {new_entries[i]} (type: {type(new_entries[i])})",
                    )

            current_entries[key] = recursive_dict_update(corresponding_entry, new_entries[i])
        else:
            raw_data_check(current_entries.get(key), new_entries)
            current_entries[key] = new_entries
    # if new_entries was a list of dictionaries, the current_entries[key] will be a dictionary instead of a list (recursive_dict_update returns a dictionary)
    # so we need to convert it back to a list
    if not isinstance(current_entries[key], list):
        current_entries[key] = [current_entries[key]]
    return current_entries


"""
This function is the main function that will be called. It will take in the current dictionary and the new dictionary, and will merge them together. A recursive
approach is used to handle nested dictionaries and lists. The function will return the merged dictionary.
"""


def recursive_dict_update(current_entries, new_entries):
    for key, new_value in new_entries.items():
        # Regular scenarios
        if new_value is None:
            continue
        # Dict and dict, so recurse
        if isinstance(new_value, dict) and (
            isinstance(current_entries.get(key), dict) or current_entries.get(key) is None
        ):
            current_entries[key] = recursive_dict_update(current_entries.get(key, {}), new_value)
        # List and list situation
        elif isinstance(new_value, list) and (
            isinstance(current_entries.get(key), list) or current_entries.get(key) is None
        ):
            current_entries = recursive_dict_update_list_helper(current_entries, key, new_value)
        # Dict and non-dict
        elif not isinstance(new_value, dict) and isinstance(current_entries.get(key), dict):
            # edge case: dict and a list, add the dict to the list
            if isinstance(new_value, list):
                new_list = new_value + [current_entries.get(key)]
                # and then now it is list, list situation
                current_entries = recursive_dict_update_list_helper(current_entries, key, new_list)
            else:
                print("dict conflict")
                print("Key: ", key)
                print("Current: ", current_entries.get(key))
                print("New: ", new_value)
        # List and non-list
        elif not isinstance(new_value, list) and isinstance(current_entries.get(key), list):
            # edge case: list and a dict, add the dict to the list
            if isinstance(new_value, dict):
                new_list = [new_value] + current_entries.get(key)
                # and then now it is list, list situation
                current_entries = recursive_dict_update_list_helper(current_entries, key, new_list)
            # edge case: one-length list and a non-list, non-dict new_value = just keep the list
            elif (
                len(current_entries.get(key)) == 1
                and not isinstance(new_value, list)
                and not isinstance(new_value, dict)
            ):
                pass
            else:
                print("list conflict")
                print("Key: ", key)
                print("Current: ", current_entries.get(key))
                print("New: ", new_value)
        else:
            raw_data_check(current_entries.get(key, None), new_value)
            current_entries[key] = new_value

    return current_entries


def main():
    all_files = [
        os.path.join(directory_path, file)
        for directory_path, _, filename in os.walk(os.path.expanduser("./"))
        for file in filename
    ]

    unified_config = {}

    # get all yaml files, except for the whitelist, and attempt to merge them
    for file in all_files:
        if file.endswith(".yaml") and file not in EXCLUDE_LIST:
            with open(file, "r") as stream:
                try:
                    config_file = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                except Exception:
                    print("Error in file: ", file)
                finally:
                    stream.close()

                unified_config = recursive_dict_update(unified_config, config_file)

    # write the unified config to a new yaml file
    with open("config-attribute-discovery-output.yaml", "w") as stream:
        try:
            yaml.dump(unified_config, stream)
        except yaml.YAMLError as exc:
            print(exc)
        except Exception as e:
            print(e)
        finally:
            stream.close()


if __name__ == "__main__":
    main()
