import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/main.py <query>")
        return
    query = sys.argv[1]
    print(f'Du hast nach "{query}" gefragt.')

if __name__ == "__main__":
    main()
