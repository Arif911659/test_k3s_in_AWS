"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Add vpc
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.10.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    )

# Add public_subnet
public_subnet = aws.ec2.Subnet("public-subnet",
vpc_id = vpc.id,
cidr_block= "10.10.1.0/24",
map_public_ip_on_launch=True, availability_zone='ap-southeast-la',
)

# Add IGW
igw = aws.ec2.InternetGateway ("igw", vpc_id=vpc.id)


# Create Route Table
route_table = aws.ec2.RouteTable("route-table",
vpc_id=vpc.id,
routes=[{
"cidr_block": "0.0.0.0/0", "gateway_id": igw.id,
}],
)
# Associate Route Table with Public Subnet
rt_assoc_public = aws.ec2.RouteTableAssociation ("rt-assoc-public",
subnet_id=public_subnet.id,
route_table_id=route_table.id,
)