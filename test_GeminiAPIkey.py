import google.generativeai as genai

genai.configure(api_key="AIzaSyCK-FkucO8ONpWyO6y4OaqHePPQPBsK5pI")

model = genai.GenerativeModel("gemini-2.5-flash-lite")
response = model.generate_content("Say hello from Gemini!")

print(response.text)