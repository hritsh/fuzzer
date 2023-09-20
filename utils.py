def get_combinations(file):
    """
    Get Combinations of filenames and extensions
    """
    f = open(file, "r")
    combs = []
    fnames = set()
    exts = set()

    for file in f.readlines():
        file = file.split('.')
        fnames.add(file[0])
        exts.add(file[1].strip())

    for fname in fnames:
        for ext in exts:
            combs.append(fname + "." + ext)
    
    f.close()
    return combs


def print_table(data):
    """
    Pretty print table data
    """
    # Determine the maximum length of each field
    max_url_len = max(len(str(d.get('url', ''))) for d in data)
    max_name_len = max(len(str(d.get('name', ''))) for d in data)
    max_value_len = max(len(str(d.get('value', ''))) for d in data)

    # Define the format for each row
    row_format = row_format = "| {{:<{}}} | {{:<{}}} | {{:<{}}} |".format(max_url_len, max_name_len, max_value_len)

    # Print the header
    header = row_format.format("URL", "Name", "Value")
    separator = "-" * (len(header) + 2)
    print(separator)
    print(header)

    # Print the data rows
    prev_url = None
    for d in data:
        url = str(d.get('url', ''))
        name = str(d.get('name', ''))
        value = str(d.get('value', ''))
        if url == prev_url: print(row_format.format("", name, value))
        else:
            print(separator)
            print(row_format.format(url, name, value))
        prev_url = url

    print(separator)