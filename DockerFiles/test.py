import re

original_string = "EN - The Curious Ken Dresdell  of Dolphin Bay (2021)"
# Extract the title using a regular expression
match = re.search(r'(?<=- ).*?(?=\()', original_string)
if match:
    title = match.group(0)
else:
    title = "caca"

print(title)