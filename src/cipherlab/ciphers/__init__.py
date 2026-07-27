from cipherlab.ciphers.affine_wrapper import AffineCipher
from cipherlab.ciphers.atbash import AtbashCipher
from cipherlab.ciphers.caesar import CaesarCipher
from cipherlab.ciphers.polybius import PolybiusCipher
from cipherlab.ciphers.vigenere import VigenereCipher

CIPHERS = {
    "caesar": CaesarCipher(),
    "atbash": AtbashCipher(),
    "polybius": PolybiusCipher(),
    "vigenere": VigenereCipher(),
    "affine": AffineCipher(),
}

__all__ = [
    "CIPHERS",
    "CaesarCipher",
    "AtbashCipher",
    "PolybiusCipher",
    "VigenereCipher",
    "AffineCipher",
]
