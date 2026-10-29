with open(r'c:\Users\COMPUTER\Documents\emr\scratch\local_appointments_app\appointment.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = 8851847
eval_start = text.find('eval("module.exports = \\"', start_idx) + len('eval("module.exports = \\"')
eval_end = text.find('sourceURL=webpack:///./views/manage/list/listView.html', eval_start)
raw = text[eval_start:eval_end]

# clean up
cleaned = raw.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
with open(r'c:\Users\COMPUTER\Documents\emr\scratch\listView_clean.html', 'w', encoding='utf-8') as out:
    out.write(cleaned)
print('Wrote listView_clean.html, length:', len(cleaned))
