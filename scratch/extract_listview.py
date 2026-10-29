with open(r'c:\Users\COMPUTER\Documents\emr\scratch\local_appointments_app\appointment.js', 'r', encoding='utf-8') as f:
    text = f.read()

marker = './views/manage/list/listView.html'
idx = text.find(marker)
if idx != -1:
    eval_idx = text.find('eval("module.exports = \\"', idx)
    end_idx = text.find('\\";\\n\\n//# sourceURL=', eval_idx)
    raw = text[eval_idx + len('eval("module.exports = \\"'):end_idx]
    # unescape
    cleaned = raw.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
    print(cleaned)
    with open(r'c:\Users\COMPUTER\Documents\emr\scratch\listView.html', 'w', encoding='utf-8') as out:
        out.write(cleaned)
else:
    print('Not found')
