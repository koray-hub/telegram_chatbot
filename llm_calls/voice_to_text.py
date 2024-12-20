import subprocess
import sys
import re
import os
#subprocess.check_output(['ls', '-l'])  # All that is technically needed...
#ffmpeg -i calis.ogg -ar 16000 calis.wav
def start_speech_to_text(input='filename',output='filename'):
    # subprocess.check_output(['cd', '/home/bot/Projects/telegram_chatbot/sound_files']) 
    #subprocess.Popen("ls", cwd="telegram_chatbot/sound_files")
    #print(subprocess.check_output(['pwd'],cwd="telegram_chatbot/sound_files") )

    #./main -m models/ggml-large-v3.bin -f samples/emre.wav --language tr
    subprocess.check_output(['ffmpeg','-y','-i',input,'-ar','16000',output],cwd="/home/bot/Projects/telegram_chatbot/sound_files")
    result=subprocess.check_output(['./main', '-m','models/ggml-large-v3.bin','-f','/home/bot/Projects/telegram_chatbot/sound_files/'+output,'--language','tr'],cwd="/home/bot/Projects/whisper.cpp")
    decoded_result = result.decode('utf-8')
    # print(decoded_result)
    # print("-----------------------------------------------------------------------")
    def extract_and_combine_text(text):
        # Split the text into lines
        lines = text.split('\n')
    
        # Regular expression to match the timestamp pattern
        timestamp_pattern = r'\[\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\]\s*'
        
        # Extract and combine the text
        extracted_text = []
        for line in lines:
            # Remove the timestamp and leading/trailing whitespace
            cleaned_line = re.sub(timestamp_pattern, '', line).strip()
            if cleaned_line:
                extracted_text.append(cleaned_line)
        
        # Join the extracted text into a single string
        return ' '.join(extracted_text)
    
    extracted_text=extract_and_combine_text(decoded_result)
    #Dosyaları silmeye yarayan komut alttadır.
    os.remove('/home/bot/Projects/telegram_chatbot/sound_files/'+output)
    os.remove('/home/bot/Projects/telegram_chatbot/sound_files/'+input)
    return extracted_text


# extracted_text=start_speech_to_text(input='calis.ogg',output="calis.wav")
# print (extracted_text)

# text=b'\n[00:00:00.120 --> 00:00:02.700]   SES DENEM\xc4\xb0 1-2-3\n\n'
# decoded_text = text.decode('utf-8')
# print(decoded_text)

# # Extract the text part using regular expression
# match = re.search(r"\]\s*(.*)", decoded_text)

# if match:
#     extracted_text = match.group(1)
#     print(extracted_text)
# else:
#     print("No text found")


# extracted_text=""
# decoded_result= "[00:00:26.300 --> 00:00:27.760]   Soracağım bir şey...\
# [00:00:27.760 --> 00:00:29.880]   Isırılan mı?\
# [00:00:29.880 --> 00:00:30.960]   Hıh hıh hıh hıh!\
# [00:00:30.960 --> 00:00:32.960]   Hıh hıh hıh hıh hıh!"
# print(decoded_result)
# print("-----------------------------------------------------------------------")

# def extract_text(input_string):
#     # Split the input string into lines
#     lines = input_string.split('\n')
    
#     # Regular expression pattern to match timestamps and brackets
#     pattern = r'^\[[\d:.]+\]\s*'
    
#     # List to store extracted text
#     extracted_text = []
    
#     # Process each line
#     for line in lines:
#         # Remove timestamps and leading/trailing whitespace
#         cleaned_line = re.sub(pattern, '', line).strip()
        
#         # Add non-empty lines to the result
#         if cleaned_line:
#             extracted_text.append(cleaned_line)
    
#     # Join the extracted text into a single string
#     return ' '.join(extracted_text)

# extracted_text = extract_text(decoded_result)
# print(extracted_text)


