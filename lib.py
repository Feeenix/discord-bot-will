from imports_and_constants import *


def copy_file(src, dst):
    shutil.copyfile(src, dst)

def load_json(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        if os.path.exists(file_name + ".old"):
            copy_file(file_name + ".old", file_name)
            with open(file_name, "r") as file:
                return json.load(file)
        else:
            raise json.decoder.JSONDecodeError("JSON file is corrupted and no backup exists", "", 0)
        
def save_json(file_name, data):
    if os.path.exists(file_name):
        copy_file(file_name, file_name + ".old")

    with open(file_name, "w") as file:
        json.dump(data, file, indent=2)

if __name__ == "__main__":
    # save_json("test.json", {"cdb": "test"})
    print(load_json("test.json"))