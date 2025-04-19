from kubernetes import client, config
import boto3
import os
from find_ext_image import *

#config.load_kube_config()  # For local running
config.load_incluster_config()  # Will use during service account
v1 = client.CoreV1Api()

ignored_substrings = {"your-excluded-pattern", "some-other-pattern"}  #To not include when fetching running images from k8s

# Specify the file paths
running_images_k8s = "running_images.txt"  
present_in_ecr = "process/processed_images.txt"    
file_to_process = "difference.txt"

try:
    running_images = process_running_images(v1, ignored_substrings, running_images_k8s)
    try:
        with open(running_images_k8s, "r") as f1:
            file1_lines = set(f1.readlines())
    except Exception as e:
        print(f"Error reading {running_images_k8s}: {e}")
        exit(1)

    try:
        with open(present_in_ecr, "r") as f2:
            file2_lines = set(f2.readlines())
    except Exception as e:
        print(f"Error reading {present_in_ecr}: {e}")
        exit(1)

    try:
        if os.path.exists(file_to_process):
            os.remove(file_to_process)
            print(f"Deleted existing file: {file_to_process}")

        # diff of items in file1_lines but not in file2_lines
        
        diff_lines = file1_lines.difference(file2_lines) 
        with open(file_to_process, "w") as diff_file:
            for line in diff_lines:
                diff_file.write(line)
                print(f"Difference written to file {file_to_process}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    if os.path.getsize(file_to_process) == 0:
        print(f"The file {file_to_process} is empty, there is nothing to process.") 
    else:
        print(f"The file {file_to_process} has content.")
        print("----------------------------------------------")
        print("Login to ECR")

        registry_url = ecr_login()
        process_line_by_line(file_to_process, registry_url)

    print("==========================================")
    print("Printing running images in cluster")
    print("==========================================")
    read_file_contents(running_images_k8s)
    print("==========================================")
    print("Printing images present in ECR")
    print("==========================================")
    read_file_contents(present_in_ecr)
    print("==========================================")
    print("File to process")
    read_file_contents(file_to_process)
    exit(0)  

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)  
