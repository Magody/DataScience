import math


def is_discrete(value):
    return int((value//1)*100) == int(value*100)

def is_real_number(x):
    global errors
    try:
        cast_x = float(x)
        if math.isnan(cast_x):
            errors['nan'] += 1
            return False
        else:
            return True
    except:
        if x not in errors:
            errors[x] = 0
        errors[x] += 1
        return False