import boto3
import click
import botocore

session = boto3.Session(profile_name="Sidharth_Gulati")
ec2 = session.resource("ec2")


def filter_instances(uni):
    instances = []

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
def cli():
    "Shots manages EC2 instances, volumes and snapshots"


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
def stop_instances(uni):
    "Stop EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Stopping {} instance ".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {}".format(i.id) + str(e))
            continue


@instances.command("start", help="Start EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
def start_instances(uni):
    "Starting EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Starting {} instance".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {}".format(i.id) + str(e))


@instances.command("terminate", help="Terminate EC2 instances")
@click.option("--uni", default=None, help="Only instances of Universe")
def terminate_instances(uni):
    "Terminate EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Terminating {} instance".format(i.id))
        i.terminate()


@instances.command("create_snapshots", help="Create Snapshots of EC2 instances")
@click.option("--uni", default=None, help="Only instances for Universe")
def create_snapshots(uni):
    "Create snapshots for all EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Stopping Instance : {}".format(i.id))
        try:
            i.stop()
            i.wait_unitl_stopped()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {}".format(i.id) + str(e))
            continue

        for v in i.volumes.all():
            if pending_snaps(v):
                print("Skipping {} - snapshot already in progress".format(v.id))
                continue
            print("Creating Snapshot of : {}".format(v.id))
            v.create_snapshots(Description="Created by Python Script")
        print("Starting Instance : {}".format(i.id))
        i.start()
        i.wait_unti_running()

    print("All Snapshots have been Created")

    return


if __name__ == "__main__":
    cli()
