import requests


def main():
    resposne = requests.get(url="http://localhost:8000/sleep/summary")
    print(resposne.json())

if __name__ == "__main__":
    main()
    