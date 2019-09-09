import boto3
import click

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


@click.group()
def instances():
    "Commands for listing"


@instances.command("list")
@click.option("--uni", default=None, help="Only instances of Universe")
def list_instances(uni):
    "List EC2 instances"

    instances = filter(uni)

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


@instances.command("stop")
@click.option("--uni", default=None, help="Only instances of Universe")
def stop_instances(uni):
    "Stop EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Stopping {} instance ".format(i.id))
        i.stop()


@instances.command("start")
@click.option("--uni", default=None, help="Only instances of Universe")
def start_instances(uni):
    "Starting EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Starting {} instance".format(i.id))
        i.start()


@instances.command("terminate")
@click.option("--uni", default=None, help="Only instances of Universe")
def terminate_instances(uni):
    "Terminate EC2 instances"

    instances = filter_instances(uni)

    for i in instances:
        print("Terminating {} instance".format(i.id))
        i.terminate()


if __name__ == "__main__":
    instances()
