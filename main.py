from faster_whisper import WhisperModel
import pyaudio
import wave
import keyboard
import time
import json
import sys
import pyautogui
import pyperclip
import winsound

model = WhisperModel("faster-whisper-small", device="cpu", compute_type="int8")
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
output_file = ".cache\\sound.wav"
is_stop = False

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)
control_key = config["control_key"]
stop_key = config["stop_key"]
quit_key = config["quit_key"]
auto_enter = config["auto_enter"]

pa = pyaudio.PyAudio()

if config["device"] == -1:
    print("未选择初始设备，请选择最大输入通道大于0的设备的编号，在目录下的config.json里的device修改-1参数，然后重新打开程序")
    print('例: "device": 1\n')
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        print(f"设备 {i}: {info['name']}, 最大输入通道: {info['maxInputChannels']}")
    sys.exit()
    
print("程序启动成功，可在config.json文件里修改录音按键(control_key)，打断按键(stop_key)，退出按键(quit_key)的值")
print(f"录音按键 {control_key} 打断按键 {stop_key} 退出按键 {quit_key}")

while True:
    if keyboard.is_pressed(control_key):

        winsound.Beep(2000, 200)
        stream = pa.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=config["device"]
        )

        frames = []
        time.sleep(0.2)
        while not keyboard.is_pressed(control_key):
            data = stream.read(chunk)
            frames.append(data)
            if keyboard.is_pressed(stop_key):
                is_stop = True
                break
        
        stream.stop_stream()
        stream.close()

        if is_stop:
            print("打断")
            is_stop = False
            winsound.Beep(500, 200)
            continue

        wf = wave.open(output_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(pa.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        winsound.Beep(2000, 200)
        segments, info = model.transcribe(
            ".cache\\sound.wav",
            hotwords="Nori",
            language="zh",
            temperature=0.2
            )
        text = ""
        for segment in segments:
            text += segment.text
        print(text)
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "k")
        pyautogui.hotkey("ctrl", "v")
        if auto_enter:
            pyautogui.hotkey("enter")

    if keyboard.is_pressed(quit_key):
        break

pa.terminate()