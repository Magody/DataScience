

with open("input.txt") as f:
    lines = f.readlines()

    out = "["
    
    for i, line in enumerate(lines):
        attr = line.split("=")[0].strip()
        out += f"\"{attr}\""
        if i < len(lines)-1:
            out += ","
    out += "]"
    with open("output.txt","w") as f_out:
        f_out.write(out)