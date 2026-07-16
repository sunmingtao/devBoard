from github3 import login

gh = login(token="")  # Replace with your GitHub token
repo = gh.repository("sunmingtao", "crawler")

# Read the contents of the root directory of the repository
for content in repo.directory_contents(""):
    name, item = content
    print(item.type, name)

# Write a new file to the repository
repo.create_file("test.txt", f"Committed from python", "Hello, World!".encode()) # Must be bytes