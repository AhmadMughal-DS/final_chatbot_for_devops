import subprocess

def get_installed_libraries():
    # Run pip freeze to get installed libraries and their versions
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)

    # Check if the subprocess ran successfully
    if result.returncode == 0:
        libraries = result.stdout
        return libraries
    else:
        return f"Error retrieving libraries: {result.stderr}"

if __name__ == "__main__":
    libraries = get_installed_libraries()
    print("Installed Libraries and Versions:")
    print(libraries)
