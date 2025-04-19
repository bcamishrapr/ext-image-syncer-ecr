# README

## Overview
This script is designed to process and compare Kubernetes container images running in a cluster against a list of processed images stored in Amazon Elastic Container Registry (ECR). It identifies differences and generates a file listing the images that need further processing.

---

## Features
- Filters container images based on a set of ignored substrings.
- Reads and compares the `running_images.txt` file (generated file) and `process/processed_images.txt` file.
- Writes the differences into `difference.txt`, which lists images to process.
- Logs into AWS ECR and processes the images from the `difference.txt` file.
- Provides summaries of:
  - Running images in the Kubernetes cluster.
  - Images present in ECR.
  - Images needing processing.

---

## Requirements
- **Python 3.x**
- **Modules**:
  - `kubernetes`: To interact with the Kubernetes API.
  - `boto3`: For AWS ECR operations.
  - `os`: For file system operations.
  - `subprocess`: For running docker cmd
- A Kubernetes ServiceAccount with proper permissions to access pod and container information.
- AWS credentials configured for accessing ECR.

---

## Configuration
### Files Used:
- **`running_images.txt`**: Generated file listing running images in the Kubernetes cluster.
- **`process/processed_images.txt`**: File containing a list of images already present in ECR.
- **`difference.txt`**: File generated to list images that require further processing.

### Substring Filtering:
You can customize the substrings to ignore by modifying the `ignored_substrings` set in the script. For example:
```python
ignored_substrings = {"dkr.ecr", "your-excluded-string"}
```
---

### Editing `process/processed_images.txt` file 

In some case, we need to manually interact with `process/processed_images.txt` file, for-ex: in-case of repository gets deleted from ECR but image is mentioned in above file. In that Case for successfully re-pushing the image to ECR, you need to delete image from file.


Change existing deployment or cronjob to run debug cmd on it and then exec into pod and delete image which you want from `process/processed_images.txt`

```yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: py-syncer-deployment
  namespace: test
spec:
  replicas: 1  
  selector:
    matchLabels:
      app: py-syncer
  template:
    metadata:
      labels:
        app: py-syncer
    spec:
      serviceAccountName: py-syncer
      containers:
      - name: py-syncer-container
        image: docker.io/your-image-name
        securityContext:
          privileged: true
        command: ["sh", "-c", "sleep 3600"]  # To make it running in a debug mode
        volumeMounts:
        - name: processed-image
          mountPath: /opt/syncer/process  
          subPath: process
      volumes:
      - name: processed-image
        persistentVolumeClaim:
          claimName: py-syncer  
      restartPolicy: Always  
```

Exec into pod:

```
k -n syncer exec -ti py-syncer-deployment-7bc4796cd8-dltct -- /bin/sh

vi process/processed_images.txt
```
