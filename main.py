import easyocr

reader = easyocr.Reader(['en'])
text = reader.readtext('screen.png', detail=0)
print(text)
