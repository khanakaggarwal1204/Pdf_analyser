import re

def clean_text(text):
    text=text.strip()
    text=re.sub(r"\t+"," ", text)
    text=re.sub(r"\n{3,}","\n\n",text)
    text=re.sub(r" {2,}", " ", text)

    cleaned_lines=[]
    for line in text.split("\n"):
        line=line.strip()

        if re.fullmatch(r"[\[\]\d\s]+", line):
            continue

        cleaned_lines.append(line)
    text="\n".join(cleaned_lines)
    
    return text

