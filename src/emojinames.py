import unicodedata

data = {}
with open("emoji-zwj-sequences.txt") as f:
  for line in f:
    if line[0] == "#" or len(line.strip()) == 0:
      continue
    data_row = line.split(";")
    data[data_row[0].strip()] = data_row[2].split("#")[0].strip()

def get_name_from_codepoint(codepoint: list[str]) -> str:
  assert type(codepoint) == list
  codepoint = [code.upper() for code in codepoint]

  if len(codepoint) == 1:
    c = int(codepoint[0], 16)
    if 0xe000 <= c <= 0xf8ff or 0xf0000 <= c <= 0xfffff:
      raise ValueError("Emoji in Private Use Area")
    return unicodedata.name(chr(c))
  else:
    try:
      return data[' '.join(codepoint)]
    except KeyError:
      pass
    
    if codepoint[-1] == "20E3":
      try:
        return "keycap: " + get_name_from_codepoint(codepoint[:-1])
      except KeyError:
        pass
    if codepoint[-1] == "FE0F":
      try:
        return get_name_from_codepoint(codepoint[:-1])
      except KeyError:
        pass      
    
    # Unknown ZWJ sequences = join the names of each emoji elements
    current = 0
    start = 0
    name = []

    while start < len(codepoint):
      if current >= len(codepoint) or codepoint[current] == "200D":
        if start == 0 and current == len(codepoint):
          raise ValueError("Unknown sequence")
        name.append(get_name_from_codepoint(codepoint[start:current]))
        start = current + 1
      current += 1
    return " + ".join(name)

def get_name(filename) -> str:
  split = filename.split(".")[0].split("_")
  match split[0]:
    case "fluentui":
      match split[1]:
        case "flat":
          return ' '.join(split[2:-1])
        case "highcontrast":
          return ' '.join(split[2:-2])
        case _:
          raise ValueError("Unknown dataset")
    case "noto-emoji":
      return get_name_from_codepoint([code.removeprefix("u") for code in split[2:]])
    case "twemoji":
      return get_name_from_codepoint(split[1].split("-"))
    case _:
      raise ValueError("Unknown dataset")