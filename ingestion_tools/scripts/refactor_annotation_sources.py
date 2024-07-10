import yaml

from common.yaml_refactor import get_files_to_refactor


def main():
    print(
        "[WARNING]: Use with caution! This script overwrites existing config files, so make sure to still manually validate the changes. Comments, formatting, anchors, extends, etc. will be lost.",
    )
    if input("Do you want to continue? (y/n): ").lower() != "y":
        return

    # Get all files to validate
    files_to_validate = get_files_to_refactor()

    if not files_to_validate:
        print("[WARNING]: No files to validate.")
        return

    for file in files_to_validate:
        try:
            with open(file, "r") as stream:
                config_data = yaml.safe_load(stream)
            file_changed = False
            # If file has annotations, refactor sources
            for entry in config_data["annotations"]:
                new_sources = []
                for source in entry["sources"]:
                    # For every source, create a new dictionary with the shape as the key
                    new_source = {}
                    new_source[source["shape"]] = source
                    source.pop("shape")
                    new_sources.append(new_source)
                entry["sources"] = new_sources
                file_changed = True
            # Don't write to file if no changes were made (to try to preserve as many comments, formatting, etc.)
            if not file_changed:
                continue
            with open(file, "w") as stream:
                yaml.dump(config_data, stream)
        except KeyError:
            continue
        except Exception as e:
            print(f"[ERROR]: {file} is not a valid YAML file.")
            print(f"[ERROR]: {e}")
            continue


if __name__ == "__main__":
    main()
