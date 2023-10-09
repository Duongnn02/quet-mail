import requests

url = 'https://graph.facebook.com/101029634680676?fields=emails,name&access_token=EAAGNO4a7r2wBABD05BPbeMKlXJNoeCRmcKgjBZBN7QZBJIrzfD7VZAg09cJUlZA23ja3bV7T7lCcI20EsObwDqV0fOdAUTLA0OqosvtEy9LLOZAmpRZCtJMVBhpHh6T1o2l53xTlf4Uuy1wKHu6QQ4whHbAcB2ZANPHrwsSkMLg6B2TlPMMnxiwZB2owcieO3HgZD'

response = requests.get(url)
print(response)
if response.status_code == 200:
    data = response.json()
    if 'name' in data:
        name = data['name']
        print(f"Name: {name}")
    if 'emails' in data:
        emails = data['emails']
        print(f"Emails: {emails}")
else:
    print('Failed to retrieve data from the URL')
