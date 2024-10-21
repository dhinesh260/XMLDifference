import xml.etree.ElementTree as ET

def strip_namespace(tag):
    return tag.split('}')[-1]  # Get the tag name without the namespace

def compare_elements(e1, e2, path=""):
    differences = {
        "Value Length Change": [],
        "New or Missing Tags": [],
        "Attribute Value Changes": [],
        "Tag Order Differences": []
    }

    # Check text content (length difference)
    if (e1.text or "").strip() != (e2.text or "").strip():
        length1 = len((e1.text or "").strip())
        length2 = len((e2.text or "").strip())
        differences["Value Length Change"].append(
            f"{path}: In file1.xml, the value is '{e1.text}' (length = {length1}).\n"
            f"    In file2.xml, the value is '{e2.text}' (length = {length2}).\n"
            f"    Difference: Value length change."
        )

    # Check attributes
    for attr in set(e1.attrib.keys()).union(e2.attrib.keys()):
        val1 = e1.attrib.get(attr)
        val2 = e2.attrib.get(attr)
        if val1 != val2:
            differences["Attribute Value Changes"].append(
                f"{path}: Attribute '{attr}' mismatch.\n"
                f"    In file1.xml: '{val1}'.\n"
                f"    In file2.xml: '{val2}'.\n"
                f"    Difference: Attribute value change."
            )

    # Compare children elements
    children1 = list(e1)
    children2 = list(e2)

    # Check for missing or extra tags
    max_children = max(len(children1), len(children2))

    for i in range(max_children):
        if i < len(children1) and i < len(children2):
            child_diffs = compare_elements(children1[i], children2[i], f"{path}/{strip_namespace(children1[i].tag)}")
            for key in differences:
                differences[key].extend(child_diffs[key])
        elif i < len(children1):
            differences["New or Missing Tags"].append(
                f"{path}/{strip_namespace(children1[i].tag)}: Tag is present in file1.xml but missing in file2.xml."
            )
        else:
            differences["New or Missing Tags"].append(
                f"{path}/{strip_namespace(children2[i].tag)}: Tag is present in file2.xml but missing in file1.xml."
            )

    return differences

def narrate_differences(file1, file2, output_file):
    # Parse the XML files
    tree1 = ET.parse(file1)
    tree2 = ET.parse(file2)

    # Get the root elements
    root1 = tree1.getroot()
    root2 = tree2.getroot()

    # Compare the root elements
    differences = compare_elements(root1, root2)

    output = []

    # Format the differences for each category
    num = 1
    if differences["Value Length Change"]:
        output.append(f"{num}. Value Length Change:")
        for diff in differences["Value Length Change"]:
            output.append(f"   {diff}")
        num += 1

    if differences["New or Missing Tags"]:
        output.append(f"{num}. New or Missing Tags:")
        for diff in differences["New or Missing Tags"]:
            output.append(f"   {diff}")
        num += 1

    if differences["Attribute Value Changes"]:
        output.append(f"{num}. Attribute Value Changes:")
        for diff in differences["Attribute Value Changes"]:
            output.append(f"   {diff}")
        num += 1

    if differences["Tag Order Differences"]:
        output.append(f"{num}. Tag Order Differences:")
        for diff in differences["Tag Order Differences"]:
            output.append(f"   {diff}")
        num += 1

    # Write the structured output to a file
    with open(output_file, 'w') as f:
        if not any(differences.values()):
            f.write("The XML files are identical.")
        else:
            f.write("\n".join(output))

# Example usage
file1 = 'file1.xml'  # Path to your first XML file
file2 = 'file2.xml'  # Path to your second XML file
output_file = 'differences_output.txt'  # Output file to write differences

narrate_differences('xml_files/' + file1, 'xml_files/' + file2, 'comparison_report/' + output_file)
