import requests
import json
import pathlib
import subprocess

# Read main configuration file to get the biome.json URL
config_path = pathlib.Path(__file__).resolve().parent.parent / "main-config.json"

with open(config_path, "r") as f:
    config = json.load(f)
    biome_config_url = config.get("biome.json_url", "")


def main():
    # Load package.json to check for Biome dependency
    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)
    except FileNotFoundError:
        return print(
            "No package.json found. Please run this script in a valid Node.js project directory."
        )

    # If biome dependency does not exist, install Biome and then initialize it
    try:
        package_data["devDependencies"]["@biomejs/biome"]
    except KeyError:
        print("Biome dependency not found. Installing it...")
        # Try to install Biome and initialize it
        subprocess.run(["pnpm", "i", "@biomejs/biome", "-D"], check=True)

    # Delete biome.json if it exists to avoid conflicts and then recreate it
    deleted_biome_json = False

    biome_json_path = pathlib.Path("biome.json")
    if biome_json_path.exists():
        biome_json_path.unlink()
        deleted_biome_json = True

    word_prefix = "Re-initializing" if deleted_biome_json else "Initializing"
    print(f"{word_prefix} Biome...")
    subprocess.run(["pnpm", "exec", "biome", "init"], check=True)

    # Read schema from the recently created biome.json
    with open("biome.json", "r") as f:
        biome_schema = json.load(f).get("$schema", None)
        if biome_schema:
            print(f"Current Biome schema loaded. {biome_schema}")
        else:
            raise Exception("Failed to read biome.json after initialization.")

    # Fetch the biome configuration from the specified URL
    biome_config = fetch_biome_configuration()
    biome_config = {"$schema": biome_schema, **biome_config}

    # Write the fetched configuration to biome.json
    with open("biome.json", "w") as f:
        json.dump(biome_config, f, indent=2)

    print("biome.json has been synchronized successfully.")


def fetch_biome_configuration():
    response = requests.get(biome_config_url)

    if response.status_code == 200:
        config = json.loads(response.text)
        return config
    else:
        raise Exception("Failed to fetch biome configuration.")


if __name__ == "__main__":
    main()
