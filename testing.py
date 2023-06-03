import difflib

def highlight_differences(str1, str2):
    diff = difflib.ndiff(str1.split(), str2.split())
    highlighted_diff = []

    for item in diff:
        if item.startswith('-'):
            highlighted_diff.append('<u><font color=\"#FF0000\">' + item[2:] + '</font></u>')
        elif item.startswith('+'):
            highlighted_diff.append('<i><font color=\"#ecb20b\">' + item[2:] + '</font></i>')
        else:
            highlighted_diff.append(item[2:])  # Exclude the + or - prefix

    return ' '.join(highlighted_diff)

# Example usage
sentence1 = "Gib mir Bier schnell!"
sentence2 = "Gib mir bitte jetzt ein Bier!"

highlighted_sentence = highlight_differences(sentence1, sentence2)
print(highlighted_sentence)

