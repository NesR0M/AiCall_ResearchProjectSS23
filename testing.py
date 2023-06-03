def highlight_diffs(original, corrected):
    original = original.replace('.', '')  # Remove periods from original sentence
    corrected = corrected.replace('.', '')  # Remove periods from corrected sentence

    original_words = original.split()
    corrected_words = corrected.split()

    result = ""
    i = 0
    j = 0
    while i < len(original_words) and j < len(corrected_words):
        if original_words[i] != corrected_words[j]:
            incorrect = []
            correct = []
            while (i < len(original_words) and j < len(corrected_words) and 
                   original_words[i] != corrected_words[j]):
                incorrect.append(original_words[i])
                correct.append(corrected_words[j])
                i += 1
                j += 1
            
            result += "<u>" + " ".join(incorrect) + "</u> "
            result += "<i>" + " ".join(correct) + "</i> "
        else:
            result += original_words[i] + " "
            i += 1
            j += 1

    # If there are remaining words in original sentence
    while i < len(original_words):
        result += "<u>" + original_words[i] + "</u> "
        i += 1

    # If there are remaining words in corrected sentence
    while j < len(corrected_words):
        result += "<i>" + corrected_words[j] + "</i> "
        j += 1

    return result

original = "Ich will essen ein Eis jetzt sofort."
corrected = "Ich will jetzt ein Eis essen sofort."
print(highlight_diffs(original, corrected))


