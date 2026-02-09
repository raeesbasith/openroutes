import google.generativeai as genai

api_key = "AIzaSyCIcgQE4YX0a-cdCEI14NX4G40VgliOAHM"
genai.configure(api_key=api_key)

print("Available models supporting generateContent:")
try:
    succeeded = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            succeeded = True
    
    if not succeeded:
        print("No models found supporting generateContent.")
        
except Exception as e:
    print(f"Error listing models: {e}")
