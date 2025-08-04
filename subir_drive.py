import requests

url = "http://repositorio.pedagogica.edu.co/bitstream/handle/20.500.12209/9559/TE-21302.pdf?sequence=1&isAllowed=y"
response = requests.get(url)

print("Código de respuesta:", response.status_code)