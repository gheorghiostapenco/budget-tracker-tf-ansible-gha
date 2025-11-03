# budget-tracker-tf-ansible-gha
Budget Tracker application (using Terraform-Ansible-DigitalOcean and GitHub Actions)

🌐 **DevOps Portfolio: Automated Budget Tracker**

<img width="718" height="836" alt="image" src="https://github.com/user-attachments/assets/86eaae82-3da3-4f1f-83d4-1961d216c8e6" />


🚀 **Project Overview**

This project showcases a fully automated solution for deploying a web application (a simple budget tracker) on DigitalOcean cloud infrastructure.

The main objective is to demonstrate proficiency across the full DevOps lifecycle, including:

Infrastructure as Code (IaC): Managing cloud resources using Terraform.

Configuration Management (CM): Server setup and Docker installation using Ansible.

Containerization: Utilizing Docker for application portability.

Continuous Integration and Continuous Deployment (CI/CD): Automating the entire process with GitHub Actions.



🏗️ **Solution Architecture**

The project utilizes the GitOps paradigm. Every merge to the main branch triggers an automatic deployment process.

Code Push (GitHub): Changes to the application code, Terraform, or Ansible are committed to the repository.

CI (GitHub Actions): The build process starts: the application is containerized (Docker), and the new image is pushed to Docker Hub.

CD (GitHub Actions):

Terraform Apply: The infrastructure (DigitalOcean Droplet and Firewall) is created or updated. The IP address of the new Droplet is extracted.

Ansible Run: Ansible connects to the Droplet via SSH, installs necessary dependencies (Docker), and runs the latest image from Docker Hub.

Deployment: The application becomes accessible via the Droplet's public IP address on port 80.

🛠️ **Technology Stack**

Category

Tools

Role in the Project

Infrastructure as Code (IaC)

Terraform

Provisioning the Droplet and configuring the Firewall on DigitalOcean.

Configuration Management (CM)

Ansible

Installing Docker, Docker Compose, and launching the application container on the remote VM.

Containerization

Docker

Packaging the application (Flask/Node.js) into a portable image.

CI/CD

GitHub Actions

Automating the entire pipeline, from build to deployment.

Cloud Provider

DigitalOcean

Hosting the infrastructure (Droplet, Firewall).

Image Registry

Docker Hub

Storing the built Docker image.

⚙️ **Detailed CI/CD Pipeline Description** (.github/workflows/main.yml)

The pipeline is split into two sequential jobs, each demonstrating core competencies.

1. build_and_push (CI)

Goal: Ensure the application is always packaged in an up-to-date Docker image and available for deployment.

Steps:

Checkout Code: Retrieve the source code.

Login to Docker Hub: Authenticate using GitHub Secrets.

Build and Push: Build the image using the Dockerfile and push it to Docker Hub with the latest tag.

2. deploy (CD)

Goal: Deploy the infrastructure and configuration using IaC and CM.

A. IaC (Terraform)

Key Step: Terraform Apply – creates or idempotently updates the Droplet and Firewall.

Integration: Uses terraform output -raw droplet_ip to dynamically extract the created machine's IP address. This IP is passed as an environment variable to the subsequent Ansible step.

B. CM (Ansible)

Connection: Uses a GitHub Secret (SSH_PRIVATE_KEY) for secure SSH connection to the Droplet.

Playbook: Executes playbook.yml, which performs:

Installation of apt dependencies.

Installation of Docker.

Installation of Docker Compose (via pip).

Container Startup: Pulls the fresh image from Docker Hub and runs it, mapping the container's port 5000 to the host's public port 80.

🔑 **Secret Configuration (GitHub Secrets)**

The following environment variables must be defined in your GitHub repository settings for the pipeline to run successfully:

Secret Name

Description

Tool

DO_TOKEN

DigitalOcean API Token. Used by Terraform for cloud management.

Terraform

DOCKER_USERNAME

Docker Hub username.

GitHub Actions (CI)

DOCKER_PASSWORD

Docker Hub token or password.

GitHub Actions (CI)

SSH_PRIVATE_KEY

Private SSH key for Droplet access. Critical for Ansible.

Ansible

💻 **Local Run and Testing**
To locally test the IaC and CM, follow these steps:

Clone the Repository:

git clone (https://github.com/gheorghiostapenco/budget-tracker-tf-ansible-gha))
cd your-repo-name


**Terraform:**

# Initialization
terraform init
# Check the plan (DO_TOKEN input will be prompted)
terraform plan -var 'ssh_key_name=YourSSHKeyName'
# Apply
terraform apply -var 'ssh_key_name=YourSSHKeyName' -auto-approve


Ansible:

# Get the IP address from Terraform output and create inventory.ini
# [webservers]
# <IP Address> ansible_user=root

# Run Playbook (use your SSH key for authentication)
ansible-playbook -i inventory.ini playbook.yml


🔗 Deployment Result

After the pipeline successfully completes, the application will be available at the following address:

Droplet IP Address: http://<Droplet IP Address from Terraform output>

Example API Endpoint: http://<Droplet IP Address>/api/transactions
