from pprint import pprint
from apryse_sdk.PDFNetPython import PDFDoc, PDFNet, Field


def extract_pdf_data(template_path: str) -> dict:
    # Initialize PDFNet
    license_key = 'demo:12345:6789'
    PDFNet.Initialize(license_key)

    # Open document
    doc = PDFDoc(template_path)

    # Extract field data
    pdf_data = {}
    itr = doc.GetFieldIterator()

    while itr.HasNext():
        field = itr.Current()
        field_type = field.GetType()
        if field_type in (Field.e_choice, Field.e_radio):
            num_options = field.GetOptCount()
            options = [field.GetOpt(i) for i in range(num_options)]
            pdf_data[field.GetName()] = options

        elif field_type == Field.e_check:
            pdf_data[field.GetName()] = field.GetValueAsBool()

        else:
            pdf_data[field.GetName()] = field.GetValueAsString()

        itr.Next()

    doc.Close()
    return pdf_data


def main():
    pdf_path = 'local_test/sample.pdf'
    pdf_data = extract_pdf_data(pdf_path)
    pprint(pdf_data)


if __name__ == '__main__':
    main()
