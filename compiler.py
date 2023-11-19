# Matin Mahmudi 99109336

from Scanner import Scanner
try:
    with open("input.txt", "r") as f:
        data = f.read()

        # Scanner
        scanner = Scanner(data)
        scanner.scan_all()

except FileNotFoundError as e:
    print("Could not find input.txt")
except Exception as e:
    # Handle other exceptions here
    print("An error occurred: ", e)
