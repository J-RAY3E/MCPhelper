def encrypt(word):
    base = ''
    encrypted = ''
    for char in word:
        if char.isalpha():
            if char.isupper():
                base += chr((ord(char) - 65 + 3) % 26 + 65)
            else:
                base += chr((ord(char) - 97 + 3) % 26 + 97)
            else:
                base += char
            encrypted += base + char
        else:
            encrypted += char
    return encrypted, base
