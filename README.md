# myBlockchain_3

<개발내용>
1. ECDSA 기반 key pair (private, public key) 생성
2. 비트코인의 주소 체계와 같은 주소 생성
3. 임의의 데이터(문자열)을 private key로 signature 생성
4. Public key를 이용하여 검증

Python으로 개발하였으며, 출력 결과는 아래와 같습니다.

--------------------------------------------------------------------------------------------------------------------------

1-1. ECDSA Private Key 생성
ECDSA Private Key:  2b2b3602bc3fc91549c2d61ee49a0c79e0636ceb60636fc348820db869605b23

1-2. ECDSA Public Key 생성
ECDSA Public Key:  0422d28d3069d06119a9e1ebbf0d7b73c0556d1c664774d0c5733d267c0de51b3456865640b3c7df3d1ec41e6a51d8c212140fb2771c8652467a0146ad9734ef04

2-1. 공개키를 RIPEMD(SHA256(PubKey)) 해싱 알고리즘으로 두 번 해싱
SHA256(ECDSA Public Key):  c309c7ede5bacec4ce853e3cdebd4fc19c9c099f10003d84c22f08696166da92
RIDEMP160(SHA256(ECDSA Public Key)):  0266f0ec504594bcb69850e54f403992068142c1

2-2. 접두에 Version '00' + Public key hash
Prepend Network Byte to RIDEMP160(SHA256(ECDSA Public Key)):  000266f0ec504594bcb69850e54f403992068142c1

2-3. 접미에 붙일 Checksum 구함
	|___>SHA256 # 1  :  2d56bff000add7658d7b0d4713c9408d4f44fe15c55df574b23b65ec017f39a4
	|___>SHA256 # 2  :  3605bcd93545f8e429c3305203efed41d5f61971fe28df8215cc95253d387b5c
Checksum(first 4 bytes):  3605bcd9

2-4. 체크섬을 접미에 추가
Append Checksum to RIDEMP160(SHA256(ECDSA Public Key)):  000266f0ec504594bcb69850e54f403992068142c13605bcd9

2-5. 비트코인의 주소 체계와 같은 주소 생성(base58로 해싱)
Bitcoin Address:  1DhfriEzm5mmeWwrJpUreA6qYTe674uQU


3~4. 임의의 문자열을 private key로 signature 생성,Public key를 이용하여 검증

임의의문자열 :  안녕하세요 우동호입니다.

전자서명 생성 :
h(x) = 0x43d7543a14c355079d14af13ef521637beaee04c61cfd16ebd1a4b1afb35e78a
   r = 0x41ddc63ee6aed95e80c0bb541ed78cdddf6b987588ce45dd4c734fc5071c3b22
   s = 0xc903b1e0753ce343659d0f69642c5ad74174c8b72863ff7f8544f2614e3e863b

전자서명 확인 :
h(x) = 0x43d7543a14c355079d14af13ef521637beaee04c61cfd16ebd1a4b1afb35e78a
   x = 0x41ddc63ee6aed95e80c0bb541ed78cdddf6b987588ce45dd4c734fc5071c3b22
   r = 0x41ddc63ee6aed95e80c0bb541ed78cdddf6b987588ce45dd4c734fc5071c3b22

* Valid Signature!
