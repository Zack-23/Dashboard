import re

filename = "RDL_2025-09-01_USB0.txt"

pattern = r"\d{4}/\d{2}/\d{2}"  # this searches for the correct date.

header = (
        "Date Std_Time Sample " # seperate headers with space
        "T01 T02 T03 T04 T05 T06 T07 T08 "
        "Teros1_mV VWC1 Pascal1 "
        "Teros2_mV VWC2 Pascal2 "
        "Teros3_mV VWC3 Pascal3 "
        "Teros4_mV VWC4 Pascal4\n"
    )

output_file = "TestingOutput.txt"

with open(filename, "r") as file, open(output_file, "w") as output:
    output.write(header)

    for line in file:
        valid_line = re.search(pattern, line)
        if not valid_line:
            continue

        clean_line = line.strip()
        parts = clean_line.split()
        cols = []
        skip_next = False

        for check in parts:
            if skip_next:
                skip_next = False
                continue

            if check == "*":
                continue

            match = re.fullmatch(pattern, check)

            if match:
                skip_next = True
                continue
            else:
                cols.append(check)

        cols = cols[:-2]

        if len(cols) != 23:
            continue

        output.write(" ".join(cols) + "\n")


