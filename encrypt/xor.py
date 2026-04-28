import os
import sys


def xor_encrypt_decrypt(data, key):
    key_len = len(key)
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key[i % key_len])
    return result


def encrypt_shellcode_from_file(input_filename, output_filename, key):
    if not os.path.exists(input_filename):
        print(f"Error: Input file {input_filename} not found.")
        return

    with open(input_filename, "rb") as f:
        raw_shellcode = bytearray(f.read())

    print(f"Read {len(raw_shellcode)} bytes from {input_filename}")

    if len(raw_shellcode) == 0:
        print("Error: Input file is empty.")
        return

    encrypted_shellcode = xor_encrypt_decrypt(raw_shellcode, key)

    with open(output_filename, "wb") as f:
        f.write(encrypted_shellcode)

    print(f"Encrypted shellcode saved to {output_filename}")


def decrypt_shellcode_from_file(input_filename, output_filename, key):
    if not os.path.exists(input_filename):
        print(f"Error: Input file {input_filename} not found.")
        return

    with open(input_filename, "rb") as f:
        encrypted_shellcode = bytearray(f.read())

    print(f"Read {len(encrypted_shellcode)} bytes from {input_filename}")

    if len(encrypted_shellcode) == 0:
        print("Error: Encrypted file is empty.")
        return

    decrypted_shellcode = xor_encrypt_decrypt(encrypted_shellcode, key)

    with open(output_filename, "wb") as f:
        f.write(decrypted_shellcode)

    print(f"Decrypted shellcode saved to {output_filename}")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <KEY> <INPUT_FILE>")
        print(f"Example: python {sys.argv[0]} mykey shellcode.bin")
        return

    key = sys.argv[1].encode()          # KEY from argument
    raw_shellcode_filename = sys.argv[2]

    encrypted_filename = "encrypted_shellcode.bin"
    decrypted_filename = "decrypted_shellcode.bin"

    encrypt_shellcode_from_file(raw_shellcode_filename, encrypted_filename, key)
    decrypt_shellcode_from_file(encrypted_filename, decrypted_filename, key)


if __name__ == "__main__":
    main()
