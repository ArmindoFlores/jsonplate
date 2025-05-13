import jsonplate


with open("test.json", "r") as f:
    text = f.read()

print(jsonplate.parse(text))
