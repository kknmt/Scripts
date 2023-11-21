# file_utils.py
def is_version_downloaded(software, version, downloaded_versions):
    """Check if the version of the software has already been downloaded."""
    return f"{software}-{version}" in downloaded_versions

def mark_version_as_downloaded(software, version, downloaded_versions, file_path):
    """Mark the version as downloaded by adding it to the downloaded_versions file."""
    with open(file_path, 'a') as file:
        file.write(f"{software}-{version}\n")
    downloaded_versions.append(f"{software}-{version}")

def save_file(response, file_path):
    """Save the downloaded file."""
    with open(file_path, 'wb') as file:
        file.write(response.content)
