file = open("../category_comparison/testing.txt", "r", encoding="utf-8")

full_text = file.read()

appeals = full_text.split("""-----------------------------------------------------------------------------

-----------------------------------------------------------------------------""")

email_count = 0
name_count = 0
surname_count = 0
category_count = 0
flag = 0

for appeal in appeals:
    flag = 0
    for letter in appeal:
        if letter == "✓":
            if flag == 0:
                email_count += 1
            elif flag == 1:
                name_count += 1
            elif flag == 2:
                surname_count += 1
            elif flag == 3:
                category_count += 1
            flag += 1
        if letter == "✗":
            flag += 1

print(email_count, " ", name_count, " ", surname_count, " ", category_count)