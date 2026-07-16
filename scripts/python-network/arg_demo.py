import argparse

parser = argparse.ArgumentParser(description="My Script")

parser.add_argument("input")
parser.add_argument("url", nargs="?")
parser.add_argument("--output", default="out.txt")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

print(args.input)
print(args.url)
print(args.output)
print(args.verbose)