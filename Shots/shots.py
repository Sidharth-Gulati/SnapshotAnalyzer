import boto3
import click
import botocore
import datetime

session = None


def filter_instances(uni="", ids=None):
    instances = []
    ec2 = session.resource("ec2")
    if uni:
        filters = [{"Name": "tag:Universe", "Values": [uni]}]
        instances = ec2.instances.filter(Filters=filters)
    if ids is not None:
        instances = ec2.instances.filter(InstanceIds=ids)
    else:
        instances = ec2.instances.all()

    return instances


def pending_snaps(volume):
    snaps = list(volume.snapshots.all())
    return snaps and snaps[0].state == "pending"


@click.group()
@click.option("--profile", default="Sidharth_Gulati", help="Setup AWS profile")
@click.option("--region", default="us-east-1", help="Setup Region for commands")
def cli(profile, region):
    "Shots manages EC2 instances, volumes and snapshots"

    global session

    if profile or region:
        try:
            session = boto3.Session(profile_name=profile, region_name=region)
        except botocore.exceptions.ProfileNotFound as e:
            raise Exception("This profile is not configured ; " + str(e))


@cli.group("snapshots")
def snapshots():
    """Commands for Snapshots"""


@snapshots.command("list", help="List Most Recent snapshots")
@click.option("--uni", default=None, help="Only snapshots of Universe")
@click.option(
    "--all", "list_all", default=False, is_flag=True, help="List all the Snapshots"
)
def list_snapshots(uni, list_all):
    "List EC2 snapshots"

    instances = filter_instances(uni)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(
                    ", ".join(
                        (
                            s.id,
                            v.id,
                            i.id,
                            s.state,
                            s.progress,
                            s.start_time.strftime("%c"),
                        )
                    )
                )
                if s.state == "completed" and not list_all:
                    break
    return


@snapshots.command("delete", help="List Most Recent snapshots")
@click.option(
    "--all", "delete_all", default=False, is_flag=True, help="List all the Snapshots"
)
def delete_snapshots(delete_all):
    "Delete EC2 snapshots"

    instances = filter_instances("")

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print("Deleting Snapshot : {}".format(s.id))
                s.delete()
    return


@cli.group("images")
def images():
    """Commands for EC2 Images"""


@images.command("list", help="List Images")
@click.option("--uni", default=None, help="Only images of Universe")
@click.option("--instance", default=None, help="Target instance by id")
def list_images(uni, instance):
    if uni:
        instances = filter_instances(uni)
    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)
    else:
        instances = filter_instances("")

    for i in instances:
        if i.image:
            print(", ".join((i.image.image_id, i.id, i.image.state)))

        else:
            continue

    return


# @images.command("dereg", help="Deregister the AMI")
# @click.option("--instance", default=None, help="Target By instance")
# @click.option("--all", default=None, help="Deregister all AMIs")
# def deregister_ami(instance, all):
#     if all:
#         instances = filter_instances("")
#     if instance:
#         ids = [].append(instance)
#         instances = filter_instances("", ids)

#     for i in instances:
#         if i.image:
#             print("Deregistering AMI : {}".format(i.image.image_id))
#             i.image.modify_attribute(
#                 Attribute="LaunchPermission",
#                 LaunchPermission={"Add": [{"Group": "all"}]},
#                 UserIds=["Sidharth_Gulati"],
#             )
#             i.image.deregister(DryRun=True)

#     return


@cli.group("volumes")
def volumes():
    """Commands for EBS volumes"""


@volumes.command("list", help="List Volumes")
@click.option("--uni", default=None, help="Only volumes of Universe")
def list_volumes(uni):
    instances = filter_instances(uni)

    for i in instances:
        for v in i.volumes.all():
            print(
                ", ".join(
                    (
                        v.id,
                        i.id,
                        v.state,
                        str(v.size) + "GiB",
                        v.encrypted and "Encrypted" or "Not Encrypted",
                    )
                )
            )

    return


@cli.group("instances")
def instances():
    """Commands for EC2 instances"""


@instances.command("list", help="List EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
def list_instances(uni):
    "List EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        tags = {t["Key"]: t["Value"] for t in i.tags or []}
        print(
            ", ".join(
                (
                    i.id,
                    i.instance_type,
                    i.placement["AvailabilityZone"],
                    i.state["Name"],
                    i.public_dns_name,
                    tags.get("Universe", "<No Universe>"),
                )
            )
        )
    return


@instances.command("stop", help="Stop EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option(
    "--force", default=False, is_flag=True, help="Force stop all instances without Tag"
)
@click.option("--instance", default=None, help="Target by Instance id")
def stop_instances(uni, force, instance):
    "Stop EC2 instances"
    if not force and not uni:
        raise Exception("No Universe tag has been provided")
    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)
    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Stopping {} instance ".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {}".format(i.id) + str(e))
            continue

    return


@instances.command("start", help="Start EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option("--force", default=False, is_flag=True, help="Force start all instances")
@click.option("--instance", default=None, help="Target by Instance id")
def start_instances(uni, force, instance):
    "Starting EC2 instances"

    if not force and not uni:
        raise Exception("No Universe Tag has been provided")

    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)
    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Starting {} instance".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {}".format(i.id) + str(e))


@instances.command("terminate", help="Terminate EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option(
    "--force", default=False, is_flag=True, help="Force terminate all instances"
)
@click.option("--instance", default=None, help="Target by Instance id")
def terminate_instances(uni, force, instance):
    "Terminate EC2 instances"
    if not force and not uni:
        raise Exception("No Universe Tag has been provided")

    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)
    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Terminating {} instance".format(i.id))
        i.terminate()


@instances.command("create_snapshots", help="Create Snapshots of EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option(
    "--force", default=False, is_flag=True, help="Force snapshot all instances"
)
@click.option("--instance", default=None, help="Target by Instance id")
@click.option("--age", default=None, help="Last snapshot age")
def create_snapshots(uni, force, instance, age):
    "Create snapshots for all EC2 instances"

    if not force and not uni:
        raise Exception("No Universe Tag has been provided")

    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)

    else:
        instances = filter_instances("")

    running_instances_ids = [
        i.id
        for i in instances.filter(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )
    ]

    running_instances = filter_instances("", running_instances_ids)

    for i in instances:
        aged_out = True
        for v in i.volumes.all():
            if age:
                snap_start_time = None
                now = datetime.datetime.now().date()
                for s in v.snapshots.all():
                    snap_start_time = s.start_time.date()
                    if snap_start_time:
                        if (now - snap_start_time).days < int(age):
                            aged_out = False

        if aged_out:
            if pending_snaps(v):
                print("Skipping {} - snapshot already in progress".format(v.id))
                continue
            print("Stopping Instance : {}".format(i.id))
            try:
                i.stop()
                i.wait_until_stopped()
            except botocore.exceptions.ClientError as e:
                print("Could not stop {}".format(i.id) + str(e))
                continue
            print("Creating Snapshot of : {}".format(v.id))
            v.create_snapshot(Description="Created by Python Script")

        for i in running_instances:
            if i.state["Name"] != "running":
                print("Starting Instance : {}".format(i.id))
                i.start()
                i.wait_until_running()

    print("All Snapshots have been Created")

    return


@instances.command("reboot", help="Reboot all EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option(
    "--all",
    "all_at_once",
    default=False,
    is_flag=True,
    help="Reboot all instances together",
)
@click.option("--force", default=False, is_flag=True, help="Force Reboot all instances")
@click.option("--instance", default=None, help="Target by Instance id")
def reboot_instances(uni, all_at_once, force, instance):
    "Reboot EC2 instances one at a time"

    if not force and not uni:
        raise Exception("No Universe Tag has been provided")

    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)

    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Rebooting instance : {}".format(i.id))
        i.reboot()
        if not all_at_once:
            i.wait_unti_running()

    return


@instances.command("image", help="Create AMI of instance")
@click.option("--uni", default=None, help="Only instances of Universe")
@click.option("--force", default=False, is_flag=True, help="Force Reboot all instances")
@click.option("--instance", default=None, help="Target by Instance id")
def image_instances(uni, force, instance):
    "Image EC2 instances one at a time"

    if not force and not uni:
        raise Exception("No Universe Tag has been provided")

    if instance:
        ids = [].append(instance)
        instances = filter_instances("", ids)

    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Imaging instance : {}".format(i.id))
        i.create_image(Name="AMI FOR " + str(i.id))

    return


@instances.command("launch", help="Launch Instance by AMI")
@click.option("--ami_id", default=None, help="Launch By AMI ID")
@click.option("--mincount", default=1, help="Min Number of instances to launch")
@click.option("--maxcount", default=1, help="Max Number of instances to launch")
@click.option("--type", default="t2.micro", help="Select the instance type")
@click.option("--keypair", default="MyPrivateKey", help="Select KeyPair")
def launch_instances(ami_id, mincount, maxcount, type, keypair):
    """Launch Instances using AMI ID"""

    ec2 = session.resource("ec2")
    instances = ec2.create_instances(
        ImageId=ami_id,
        InstanceType=type,
        KeyName=keypair,
        MinCount=mincount,
        MaxCount=maxcount,
    )

    list_instances("")

    return


if __name__ == "__main__":
    cli()
