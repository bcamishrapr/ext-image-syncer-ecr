from kubernetes import client, config
import boto3
from botocore.exceptions import ClientError
import subprocess

#Use to extract running images
def process_running_images(k8s_client, ignored_substrings, output_file):

    pods = k8s_client.list_pod_for_all_namespaces(watch=False)
    
    # Collect running images, ignoring those with the specified substring
    print("Collecting External Running Images from k8s-cluster")
    running_images = set()
    for pod in pods.items:
        for container in pod.status.container_statuses or []:
            if container.state.running:  # Check if the container is running
                image = container.image
                if (not any(substring in image for substring in ignored_substrings)) and not image.startswith("sha256"): # Exclude images with the substring
                    running_images.add(image)

    # Write results to the specified output file
    print("Writing Running Images to file")
    with open(output_file, "w") as file:
        for image in running_images:
            parts = image.split(":")
            if len(parts) == 2:
                image_name, image_tag = parts
            else:
                image_name = parts[0]  # In case there's no tag
                image_tag = "latest"  # Assign 'latest' as default tag

            # Write to file with '|' as the delimiter
            file.write(f"{image_name}|{image_tag}\n")

    print(f"Cluster Running Images written to {output_file}")
    return running_images

def run_command(command):
    try:
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if "Image is up to date" in result.stdout or "Downloaded newer image" in result.stdout:
            return True  # Consider this a successful run
        return True  # Success by default if no errors occurred
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        return False

def ecr_login():
     
     ecr_client = boto3.client('ecr')
     region_name = boto3.Session().region_name

     try:
         response = ecr_client.describe_registry()
         registry_url = response['registryId'] + ".dkr.ecr." + boto3.Session().region_name + ".amazonaws.com"
         print(f"Registry URL: {registry_url}")
     except Exception as e:
         print(f"Error fetching registry URL: {e}")
     
     print(f"Login to ECR: {registry_url}")
     subprocess.run(
         f"aws ecr get-login-password --region {region_name} | podman login --username AWS --password-stdin  {registry_url}",
         shell=True,
         check=True
     )
     return registry_url

def read_file_contents(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_line_by_line(file_path, registry_url):
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()

                # Split the line into image and tag using '|' as the delimiter
                if "|" in line:
                    image_path, tag = line.split("|", 1) 

                    # Extract the content after the first '/' as the image
                    image = "/".join(image_path.split("/")[1:])

                    print("==========================================")
                    print(f"image_path = {image_path}")
                    print(f"tag = {tag}")
                    
                    #Creating repository name
                    repository_name = f"development/thirdparty/{image}"
                    print(f"repository_name = {repository_name}")
                    
                    #creating ECR client 
                    ecr_client = boto3.client('ecr')
                    ecr_image = f"{registry_url}/{repository_name}:{tag}"   

                    try:
                      response = ecr_client.create_repository(
                          repositoryName=repository_name,
                          imageScanningConfiguration={'scanOnPush': True},
                          imageTagMutability='IMMUTABLE',
                          tags=[{'Key': 'Source', 'Value': 'python_syncer'}]
                      )
                      print("Repository created successfully!")
                      print("Repository details:")
                      print(f" - Name: {response['repository']['repositoryName']}")
                      print(f" - ARN: {response['repository']['repositoryArn']}")
                      print(f" - URI: {response['repository']['repositoryUri']}")
                    except ClientError as e:
                        if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
                            print(f"The repository '{repository_name}' already exists.")  
                    except Exception as e:
                      print(f"An error occurred: {e}")

                    try:
                      processed_file = "process/processed_images.txt"
                      ext_image = f"{image_path}|{tag}"

                      if run_command(f"podman pull {image_path}:{tag}"):
                         if run_command(f"podman tag {image_path}:{tag} {ecr_image}"):
                             if subprocess.run(f"podman push {ecr_image}", shell=True).returncode == 0:
                                 print(f"Image successfully pushed to ECR: {ecr_image}")

                                 with open(processed_file, "a") as processed:
                                     processed.write(f"{ext_image}\n")
                                     print(f"successfully write {ext_image} into {processed_file}")
                             else:
                                 print(f"Failed to push image: {ext_image}")
                         else:
                            print(f"Failed to tag image: {ext_image}")
                      else:
                          print(f"Failed to pull image: {ext_image}")
                    except:
                      print(f"Error: running in podman cmd")

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
