import os
import shutil


def organize_files(path):

    for file in os.listdir(path):

        file_path = os.path.join(path, file)


        if os.path.isfile(file_path):

            if file.endswith((".jpg", ".png")):
                folder = "images"

            elif file.endswith(".pdf"):
                folder = "pdf"

            elif file.endswith(".mp4"):
                folder = "videos"

            else:
                continue


            folder_path = os.path.join(
                path,
                folder
            )


            if not os.path.exists(folder_path):
                os.mkdir(folder_path)


            shutil.move(
                file_path,
                folder_path
            )