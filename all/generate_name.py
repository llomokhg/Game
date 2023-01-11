from random import randrange, choice


def generate():
    consonants = list('wrtpsdfghjklzcvbnm')
    vowels = list('euioa')
    name = ''
    for letter in range(randrange(4, 8)):
        if letter % 2 == 0:
            name += choice(consonants)
        else:
            name += choice(vowels)
            if randrange(10) <= 3:
                name += choice(vowels)
    if name[-1] in consonants:
        name += 'y'
    return name.capitalize()
