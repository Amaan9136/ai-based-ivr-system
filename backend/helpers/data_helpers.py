import csv

def save_admission_request(data):
    with open('admissions.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["student_name", "phone", "address"])
        writer.writerow(data)