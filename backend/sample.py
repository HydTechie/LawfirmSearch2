import hashlib
def reverse_string(s):
    """
    Returns the reverse of the input string s.
    """
    return s[::-1]

## q: what is the recursion?
# A: Recursion is a programming technique where a function calls itself in order to solve a problem.

def encrypt_password(password):
    # Use SHA-256 hashing
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()
# Example usage
if __name__ == "__main__":
    pwd = "mysecretpassword"
    encrypted = encrypt_password(pwd)
    print(f"Encrypted password: {encrypted}")