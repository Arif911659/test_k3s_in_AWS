"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import os
# Add vpc
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": "my-vpc-name"  # Replace "my-vpc-name" with the desired name
        }
    )

# Add public_subnet
# public_subnet = aws.ec2.Subnet("public-subnet",
#     vpc_id = vpc.id,
#     cidr_block= "10.10.1.0/24",
#     map_public_ip_on_launch=True, 
#     availability_zone='ap-southeast-la',
#     )
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.10.1.0/24",
    availability_zone="ap-southeast-1a",  # Use a valid availability zone
    tags={
        "Name": "public-subnet",
    }
)


# Adding the Internet Gateway with a Name tag
igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
    tags={
        "Name": "my-igw-name"  # Replace with your desired IGW name
    }
)

# Create Route Table
route_table = aws.ec2.RouteTable("route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0", 
        "gateway_id": igw.id,
    }],
)
# Associate Route Table with Public Subnet
rt_assoc_public = aws.ec2.RouteTableAssociation("rt-assoc-public",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id,
)


# Create Security Group
security_group = aws.ec2.SecurityGroup("web-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[
        {
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        }],
)


# Create instances in the VPC and subnet
ami_id = "ami-01811d4912b4ccb26" # Replace with a valid AMI ID for your region
instance_type = "t3.small"


# Read the public key from the environment (set by GitHub Actions).
public_key = os.getenv("PUBLIC_KEY")

# Create the EC2 KeyPair using the public key 
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair", 
    public_key=public_key)

# Create instances for Master-Node
master_node = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name, # Replace with a valid key_pair.key_name
    vpc_security_group_ids=[security_group.id],
    tags={
    "Name": "master-node"
})


# Export outputs
pulumi.export("master_public_ip", master_node.public_ip)