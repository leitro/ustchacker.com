import markdown2
import html

whiteList = [
    ('<code>', '{[(HACKERCODESTART)]}'),
    ('</code>', '{[(HACKERCODEEND)]}'),
    ('<pre>', '{[(HACKERPRESTART)]}'),
    ('</pre>', '{[(HACKERPREEND)]}'),
]


def translate(md):
    for i in whiteList:
        if i[0] in md:
            md = md.replace(i[0], i[1])
    md2 = html.escape(md)
    data = markdown2.markdown(md2)
    for i in whiteList:
        if i[1] in data:
            data = data.replace(i[1], i[0])
    return data
