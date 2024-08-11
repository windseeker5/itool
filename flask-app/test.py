import subprocess

# Run the ss command to count the number of connections on port 5000
result = subprocess.run(['ss', '-anp'], stdout=subprocess.PIPE, text=True)

connections = result.stdout.split('\n')
connections = len([c for c in connections if ':5000 ' in c])

print(f"Number of connections on port 5000: {connections}")
