import zhtts
# from playsound import playsound

text = "帮我预约个醉小酒馆餐厅"
tts = zhtts.TTS() # use fastspeech2 by default
tts.text2wav(text, "demo.wav")

import winsound
winsound.PlaySound('demo.wav', winsound.SND_FILENAME)

# import pyttsx3
# engine = pyttsx3.init()
# engine.say("帮我预约个醉小酒馆餐厅")
# engine.runAndWait()