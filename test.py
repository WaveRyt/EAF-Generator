import win32com.client

word = win32com.client.Dispatch("Word.Application")
print(word.Version)
word.Quit()