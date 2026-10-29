import re

with open(r'c:\Users\COMPUTER\Documents\emr\scratch\local_appointments_app\appointment.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('appointment-action-btn-container')
if idx != -1:
    print('Found toolbar at index', idx)
    print('--- SNIPPET ---')
    print(text[idx-100:idx+2500])
else:
    print('Not found')
