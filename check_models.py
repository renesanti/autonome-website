from google import genai

client = genai.Client()

print("Beschikbare modellen voor jouw API key:")
for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(model.name)
