# Variable for the region (can be changed without modifying main.tf)
variable "do_region" {
  description = "The region to deploy the Droplet in"
  type        = string
  default     = "nyc3"
}