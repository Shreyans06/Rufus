from rufus import RufusClient

client = RufusClient("privatekey")
prompt = "Explain the information"
documents = client.scrape("https://www.example.com" , prompt)
print(documents)