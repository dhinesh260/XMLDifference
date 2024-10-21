import xml.etree.ElementTree as ET
import sys

def strip_namespace(tag):
    return tag.split('}')[-1]  # Get the tag name without the namespace

def compare_elements(e1, e2, path=""):
    differences = {
        "Attribute Value/Length Change": [],
        "New or Missing Tags": [],
        "Tag Order Differences": [],
        "Child Differences": {}
    }

    # Check text content (length difference)
    if (e1.text or "").strip() != (e2.text or "").strip():
        length1 = len((e1.text or "").strip())
        length2 = len((e2.text or "").strip())
        differences["Attribute Value/Length Change"].append(
            f"{path}: Value length difference.\n"
            f"    In file1.xml, the value is '{e1.text}' (length = {length1}).\n"
            f"    In file2.xml, the value is '{e2.text}' (length = {length2})."
        )

    # Check attributes
    for attr in set(e1.attrib.keys()).union(e2.attrib.keys()):
        val1 = e1.attrib.get(attr)
        val2 = e2.attrib.get(attr)
        if val1 != val2:
            differences["Attribute Value/Length Change"].append(
                f"{path}: Attribute '{attr}' mismatch.\n"
                f"    In file1.xml: '{val1}'.\n"
                f"    In file2.xml: '{val2}'."
            )

    # Compare children, taking into account tag order and missing tags
    children1 = list(e1)
    children2 = list(e2)

    tags1 = [strip_namespace(child.tag) for child in children1]
    tags2 = [strip_namespace(child.tag) for child in children2]

    # Check if there are missing tags
    for tag in set(tags1).difference(tags2):
        differences["New or Missing Tags"].append(
            f"{path}: Tag '{tag}' is missing in file2.xml."
        )
    for tag in set(tags2).difference(tags1):
        differences["New or Missing Tags"].append(
            f"{path}: Tag '{tag}' is missing in file1.xml."
        )

    # Check if there are tag order differences
    if tags1 != tags2:
        differences["Tag Order Differences"].append(
            f"{path}: Tag order differs.\n"
            f"    In file1.xml: {tags1}.\n"
            f"    In file2.xml: {tags2}."
        )

    # Compare children elements recursively
    for child1, child2 in zip(children1, children2):
        child_diffs = compare_elements(child1, child2, f"{path}/{strip_namespace(child1.tag)}")
        for key in differences.keys():
            if isinstance(differences[key], list) and isinstance(child_diffs[key], list):
                differences[key].extend(child_diffs[key])

    # Count child tags only if parent counts match
    if len(children1) == len(children2):
        child_counts = {}
        for tag in set(tags1):
            count1 = tags1.count(tag)
            count2 = tags2.count(tag)
            if count1 != count2:
                child_counts[tag] = (count1, count2)

        if child_counts:
            differences["Child Differences"][strip_namespace(e1.tag)] = child_counts

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
    if differences["Attribute Value/Length Change"]:
        output.append(f"{num}. Attribute Value/Length Change:")
        for diff in differences["Attribute Value/Length Change"]:
            output.append(f"   {diff}")
        num += 1

    if differences["New or Missing Tags"]:
        output.append(f"{num}. New or Missing Tags:")
        for diff in differences["New or Missing Tags"]:
            output.append(f"   {diff}")
        num += 1

    if differences["Tag Order Differences"]:
        output.append(f"{num}. Tag Order Differences:")
        for diff in differences["Tag Order Differences"]:
            output.append(f"   {diff}")
        num += 1

    if differences["Child Differences"]:
        output.append(f"{num}. Child Differences:")
        for parent, counts in differences["Child Differences"].items():
            for tag, (count1, count2) in counts.items():
                output.append(f"   {parent} has {count1} child ({tag}) tags in file1.xml but {count2} in file2.xml.")

    # Write the structured output to a file
    with open(output_file, 'w') as f:
        if not any(differences.values()):
            f.write("The XML files are identical.")
        else:
            f.write("\n".join(output))

if __name__ == '__main__':
    print('Given arguments: ', sys.argv)
    print('# of arguments: ', len(sys.argv))
    if len(sys.argv) == 4:
        file1 = 'xml_files/' + sys.argv[1]
        file2 = 'xml_files/' + sys.argv[2]
        output_file = 'comparison_report/' + sys.argv[3]

        narrate_differences(file1, file2, output_file)
        print('Comparison report created.')
    else:
        print('Three arguments must be provided: 1. file1 name, 2. file2 name, 3. output file name')
        sys.exit()