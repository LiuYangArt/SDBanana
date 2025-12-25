import json
import sys

PLUGIN_INFO_FILE = "pluginInfo.json"


def get_version():
    with open(PLUGIN_INFO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("version", "0.0.0")


def set_version(new_version):
    with open(PLUGIN_INFO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["version"] = new_version

    with open(PLUGIN_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def parse_version(v_str):
    parts = v_str.split(".")
    return [int(p) for p in parts]


def bump_version(v_str, v_type):
    major, minor, patch = parse_version(v_str)
    if v_type == "patch":
        patch += 1
    elif v_type == "minor":
        minor += 1
        patch = 0
    elif v_type == "major":
        major += 1
        minor = 0
        patch = 0
    return f"{major}.{minor}.{patch}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python version_manager.py [info|update <type>|get]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "info":
        current = get_version()
        try:
            ma, mi, pa = parse_version(current)
            next_patch = f"{ma}.{mi}.{pa+1}"
            next_minor = f"{ma}.{mi+1}.0"
            next_major = f"{ma+1}.0.0"

            with open("versions.bat", "w") as f:
                f.write(f"set CURRENT_VERSION={current}\n")
                f.write(f"set NEXT_PATCH={next_patch}\n")
                f.write(f"set NEXT_MINOR={next_minor}\n")
                f.write(f"set NEXT_MAJOR={next_major}\n")
        except Exception as e:
            print(f"Error parsing version: {e}")
            sys.exit(1)

    elif command == "update":
        if len(sys.argv) < 3:
            print("Usage: python version_manager.py update [patch|minor|major]")
            sys.exit(1)

        v_type = sys.argv[2]
        current = get_version()
        new_v = bump_version(current, v_type)
        set_version(new_v)
        print(f"Updated version to {new_v}")

    elif command == "get":
        current = get_version()
        with open("new_version.bat", "w") as f:
            f.write(f"set NEW_VERSION={current}\n")


if __name__ == "__main__":
    main()
