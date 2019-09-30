from setuptools import setup

setup(
    name="SnapshotAnalyzer",
    version="1.0",
    author="Sidharth Gulati",
    author_email="gulatisidharth107@gmail.com",
    description="SnapshotAnalyzer manages EC2 instances, volumes and snapshots",
    license="GPLv3+",
    packages=["Shots"],
    url="https://github.com/Sidharth-Gulati/SnapshotAnalyzer",
    install_requires=["boto3", "click"],
    entry_points="""
    [console_scripts]
    shots=Shots.shots:cli""",
)
