import xmltodict
from deepdiff import DeepDiff

def compare_xml(file1, file2):
    # Read and parse the XML files
    with open(file1) as f1, open(file2) as f2:
        xml1 = xmltodict.parse(f1.read())
        xml2 = xmltodict.parse(f2.read())

    # Get the differences
    differences = DeepDiff(xml1, xml2, ignore_order=True)

    # Prepare a human-readable output
    output = []
    
    if differences:
        for change_type, changes in differences.items():
            output.append(f"{change_type}:")

            for change in changes:
                if isinstance(change, dict) and 'path' in change:
                    output.append(f"  - {change['path']}: {change.get('new_value', 'removed')} (was {change.get('old_value', 'missing')})")
                else:
                    output.append(f"  - {change}")

    else:
        output.append("The XML files are identical.")

    return "\n".join(output)

# Example usage
file1 = 'file1.xml'  # Path to your first XML file
file2 = 'file2.xml'  # Path to your second XML file

result = compare_xml(file1, file2)
print(result)

# Optionally, write the result to a file
with open('xml_comparison_output.txt', 'w') as f:
    f.write(result)
