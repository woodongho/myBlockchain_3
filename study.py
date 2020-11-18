"""
<개발내용>
1. ECDSA 기반 key pair (private, public key) 생성 - ok
2. 비트코인의 주소 체계와 같은 주소 생성 - ok
3. 임의의 데이터(문자열)을 private key로 signature 생성 - ok
4. Public key를 이용하여 검증 - ok
"""

import math
import random
from Crypto.Hash import SHA256
import ecdsa
import base58
import binascii
import hashlib

# 1-1. ECDSA Private Key 생성
print("\n\n1-1. ECDSA Private Key 생성")
ecdsaPrivateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
print("ECDSA Private Key: ", ecdsaPrivateKey.to_string().hex())
print("")

# 1-2. ECDSA Public Key 생성
print("1-2. ECDSA Public Key 생성")
ecdsaPublicKey = '04' + ecdsaPrivateKey.get_verifying_key().to_string().hex()
print("ECDSA Public Key: ", ecdsaPublicKey)
print("")

# 2-1. 공개키를 RIPEMD(SHA256(PubKey)) 해싱 알고리즘으로 두 번 해싱
print("2-1. 공개키를 RIPEMD(SHA256(PubKey)) 해싱 알고리즘으로 두 번 해싱")
hash256FromECDSAPublicKey = hashlib.sha256(binascii.unhexlify(ecdsaPublicKey)).hexdigest()
print("SHA256(ECDSA Public Key): ", hash256FromECDSAPublicKey)
ridemp160FromHash256 = hashlib.new('ripemd160', binascii.unhexlify(hash256FromECDSAPublicKey))
print("RIDEMP160(SHA256(ECDSA Public Key)): ", ridemp160FromHash256.hexdigest())
print("")

# 2-2. 접두에 Version '00' 붙이고
print("2-2. 접두에 Version '00' + Public key hash")
prependNetworkByte = '00' + ridemp160FromHash256.hexdigest()
print("Prepend Network Byte to RIDEMP160(SHA256(ECDSA Public Key)): ", prependNetworkByte)
print("")

# 2-3. 접미에 붙일 Checksum 구함
print("2-3. 접미에 붙일 Checksum 구함")
hash = prependNetworkByte
for x in range(1, 3):
    hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
    print("\t|___>SHA256 #", x, " : ", hash)
cheksum = hash[:8]
print("Checksum(first 4 bytes): ", cheksum)
print("")

# 2-4. 체크섬을 접미에 추가
print("2-4. 체크섬을 접미에 추가")
appendChecksum = prependNetworkByte + cheksum
print("Append Checksum to RIDEMP160(SHA256(ECDSA Public Key)): ", appendChecksum)
print("")

# 2-5. 비트코인의 주소 체계와 같은 주소 생성(base58로 해싱)
print("2-5. 비트코인의 주소 체계와 같은 주소 생성(base58로 해싱)")
bitcoinAddress = base58.b58encode(binascii.unhexlify(appendChecksum))
print("Bitcoin Address: ", bitcoinAddress.decode('utf8'))
print("")

# 3-1. 임의의 데이터(문자열)을 private key로 signature 생성, Public key를 이용하여 검증

# secp256k1의 Domain parameters
# y^2 = x^3 +7 mod m
a = 0
b = 7
m = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


# Additive Operation
def addOperation(a, b, p, q, m):
    if q == (math.inf, math.inf):
        return p

    x1 = p[0]
    y1 = p[1]
    x2 = q[0]
    y2 = q[1]

    if p == q:
        # Doubling
        # slope (s) = (3 * x1 ^ 2 + a) / (2 * y1) mod m
        # 분모의 역원부터 계산한다.(by Fermat`s Little Theorem)
        # pow() 함수가 내부적으로 Square-and-Multiply 알고리즘을 수행한다.
        r = 2 * y1
        rInv = pow(r, m-2, m)  # Fermat`s Little Theorem
        s = (rInv * (3 * (x1 ** 2) + a)) % m
    else:
        r = x2 - x1
        rInv = pow(r, m-2, m)
        s = (rInv * (y2 - y1)) % m
    x3 = (s ** 2 - x1 - x2) % m
    y3 = (s * (x1 - x3) - y1) % m
    return x3, y3


# 개인키를 생성한다.
def generatePrivKey():
    while(1):
        d = random.getrandbits(256)
        if d > 0 & d < n:
            break
    return d


# 공개키를 생성한다.
def generatePubKey(d, g):
    bits = bin(d)
    bits = bits[2:len(bits)]

    # initialize.bits[0] = 1 (always)
    K = g

    # 두 번째 비트부터 Double-and-Add
    bits = bits[1:len(bits)]
    for bit in bits:
        # Double
        K = addOperation(a, b, K, K, m)

        # Multiply
        if bit == '1':
            K = addOperation(a, b, K, g, m)
    return K


# 서명할 문서(임의의 데이터)
message = "안녕하세요 우동호입니다."
message = message.encode()

# 서명자의 개인키와 공개키를 생성한다.
d = generatePrivKey()
Q = generatePubKey(d, G)

# ephemeral 키를 생성한다.
k = generatePrivKey()
x, y = generatePubKey(k, G)
r = x % n

# Signing
h = SHA256.new()
h.update(message)
hx = h.hexdigest()
hx = int(hx, 16)

invK = pow(k, n-2, n)  # Fermat`s Little Theorem
s = ((hx + d * r) * invK) % n

# 전자서명을 보낸다.
print("\n3~4. 임의의 문자열을 private key로 signature 생성,Public key를 이용하여 검증")
print("\n임의의문자열 : ", message.decode())
print("\n전자서명 생성 :")
print("h(x) =", hex(hx))
print("   r =", hex(r))
print("   s =", hex(s))

# Verification
w = pow(s, n-2, n)
u1 = (w * hx) % n
u2 = (w * r) % n
v1 = generatePubKey(u1, G)
v2 = generatePubKey(u2, Q)
x, y = addOperation(a, b, v1, v2, m)

print("\n전자서명 확인 :")
print("h(x) =", hex(hx))
print("   x =", hex(x))
print("   r =", hex(r))

if r == x % n:
    print("\n* Valid Signature!")
else:
    print("\n* Invalid Signature!")
