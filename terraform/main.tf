## 0. Terraform and DigitalOcean Provider Block
################################################

# Terraform Block: Specifies the required provider and its source
terraform {
  required_providers {
    # Explicitly specify the Source Address for the DigitalOcean provider
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0" # Use a stable version range
    }
  }
}

# Provider Block: Configures the connection to DigitalOcean
provider "digitalocean" {
  # Token is securely read from the DIGITALOCEAN_TOKEN environment variable.
}


## 1. Data Source: Fetches information about your SSH key
#########################################################
data "digitalocean_ssh_key" "default" {
  # Ensure this name exactly matches the key added in DigitalOcean UI
  name = "digitaloceankey"
}


## 2. Resource: Creates a DigitalOcean Firewall
################################################
resource "digitalocean_firewall" "web_server_fw" {
  name = "web-server-firewall"

  # INBOUND RULES (Security Group)

  # 1. SSH Access (TCP, port 22) - CRITICAL for administrative access and Ansible
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"] # Allow SSH from anywhere (can be restricted to a specific IP)
  }

  # 2. HTTP Access (TCP, port 80) - Required for public web access to the application
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # 3. HTTPS Access (TCP, port 443) - Good practice for future secure communication
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # OUTBOUND RULES

  # Outbound TCP (Allow all TCP traffic out)
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535" # All ports required by the DO provider for full outbound TCP
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Outbound UDP (Allow all UDP traffic out)
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535" # All ports required by the DO provider for full outbound UDP
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Outbound ICMP (Required for pings, health checks, etc.)
  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Apply the firewall to the created Droplet resource
  droplet_ids = [digitalocean_droplet.web_server.id]
}


## 3. Resource: Creates a DigitalOcean Droplet (Virtual Server)
###############################################################
resource "digitalocean_droplet" "web_server" {
  name   = "minimal-budget-tracker"
  size   = "s-1vcpu-1gb"      # Minimum tariff size
  region = "nyc3"             # Region 
  image  = "ubuntu-22-04-x64" # OS Image

  # Attaches the previously fetched SSH key
  ssh_keys = [data.digitalocean_ssh_key.default.id]

  # NOTE: The firewall is attached via the 'digitalocean_firewall' resource block (droplet_ids).
}


## 4. Output: Displays the public IP address
###############################################################
output "web_server_ip_address" {
  description = "Public IPv4 address of the web server Droplet"
  # Get the public IPv4 address from the created Droplet attributes
  value = digitalocean_droplet.web_server.ipv4_address
}