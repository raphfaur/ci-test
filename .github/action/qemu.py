import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("--name")

args = parser.parse_args()

name = args.name

if name == "bob" :
    sys.exit(0)
else :
    sys.exit(1)