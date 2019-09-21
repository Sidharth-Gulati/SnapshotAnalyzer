import boto3
import click
import botocore
import time
import calendar

session = None
region = None


def filter_instances(uni):
    instances = []
    ec2 = session.resource("ec2")
    if uni:
        filters = [{"Name": "tag:Universe", "Values": [uni]}]
        instances = ec2.instances.filter(Filters=filters)
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
    global region
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
        instances = ec2.instances.filter(InstanceIds=ids)
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
        instances = ec2.instances.filter(InstanceIds=ids)
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
        instances = ec2.instances.filter(InstanceIds=ids)
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
        instances = ec2.instances.filter(InstanceIds=ids)

    else:
        instances = filter_instances("")

    running_instances = instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    for i in instances:
        aged_out = True
        for v in i.volumes.all():
            if age:
                utc_start_time = None
                now = calendar.timegm(time.gmtime())
                time_delta = now - (86400 * int(age))
                for s in v.snapshots.all():
                    gmt_start_time = s.start_time.strftime("%b %d, %Y @ %H:%M:%S UTC")
                    utc_start_time = calendar.timegm(
                        time.strptime(gmt_start_time, "%b %d, %Y @ %H:%M:%S UTC")
                    )
                    if s.state == "completed":
                        break
                    if utc_start_time:
                        if int(utc_start_time) > int(time_delta):
                            aged_out = False
        if aged_out:
            if pending_snaps(v):
                print("Skipping {} - snapshot already in progress".format(v.id))
                continue
            print("Stopping Instance : {}".format(i.id))
            try:
                i.stop()
                i.wait_unitl_stopped()
            except botocore.exceptions.ClientError as e:
                print("Could not stop {}".format(i.id) + str(e))
                continue
            print("Creating Snapshot of : {}".format(v.id))
            v.create_snapshots(Description="Created by Python Script")
        if i in running_instances:
            print("Starting Instance : {}".format(i.id))
            i.start()
            i.wait_unti_running()

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
        instances = ec2.instances.filter(InstanceIds=ids)

    else:
        instances = filter_instances(uni)

    for i in instances:
        print("Rebooting instance : {}".format(i.id))
        i.reboot()
        if not all_at_once:
            i.wait_unti_running()

    return


if __name__ == "__main__":
    cli()
