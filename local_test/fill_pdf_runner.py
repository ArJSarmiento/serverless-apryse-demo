from handler import fill_pdf


def main():
    event = {
        'user_id': '12345',
        'template_key': 'sample.pdf',
        'pdf_data': {
            'name': 'Test User Smith',
            'dropdownChoice': 'Choice 2',
            'checkbox1': True,
            'checkbox2': False,
            'checkbox3': True,
            'nameOfDependant': 'Jane Smith',
            'ageOfDependant': '10',
        },
    }
    print(fill_pdf(event, None))


if __name__ == '__main__':
    main()
