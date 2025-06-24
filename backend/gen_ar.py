from gtts import gTTS

# Your Arabic text
text = "ابحث لي عن تفاحة"
language = 'ar'  # Arabic

# Generate speech
tts = gTTS(text=text, lang=language)

# Save to a file
tts.save("apple_fin1_ar.mp3")

print("Audio saved")
