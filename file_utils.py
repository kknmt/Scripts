import os

def is_version_downloaded(software_name, version, downloaded_versions_set):
    combined_version = f"{software_name}-{version}"
    return combined_version in downloaded_versions_set

def mark_version_as_downloaded(software_name, version, downloaded_versions_set, downloaded_versions_file):
    combined_version = f"{software_name}-{version}"
    downloaded_versions_set.add(combined_version)
    with open(downloaded_versions_file, "a") as file:
        file.write(f"{combined_version}\n")

def save_file(response, file_path):
    # ファイル保存先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(response.content)
