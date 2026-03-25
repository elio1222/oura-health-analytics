import requests


def main():
    resposne = requests.get(url="http://0.0.0.0:8000/stress/summary/")
    print(resposne.json())

if __name__ == "__main__":
    main()
