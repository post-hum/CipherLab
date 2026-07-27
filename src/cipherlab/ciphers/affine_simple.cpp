#include <iostream>
#include <string>
#include <fstream>
#include <algorithm>
#include <cctype>
#include <clocale>

using namespace std;

const string ALPHABET_LOWER = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя";
const string ALPHABET_UPPER = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";

int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int modInverse(int a, int m) {
    for (int i = 0; i < m; i++) {
        if ((a * i) % m == 1)
            return i;
    }
    return -1;
}

string encrypt(const string& text, int a, int b) {
    int m = ALPHABET_LOWER.size();
    string result;
    
    for (char c : text) {
        size_t pos = ALPHABET_LOWER.find(c);
        if (pos != string::npos) {
            int x = (a * pos + b) % m;
            result += ALPHABET_LOWER[x];
        }
        else {
            pos = ALPHABET_UPPER.find(c);
            if (pos != string::npos) {
                int x = (a * pos + b) % m;
                result += ALPHABET_UPPER[x];
            }
            else {
                result += c;
            }
        }
    }
    return result;
}

string decrypt(const string& text, int a, int b) {
    int m = ALPHABET_LOWER.size();
    int inv = modInverse(a, m);
    
    if (inv == -1) {
        return "ERROR: no inverse";
    }
    
    string result;
    for (char c : text) {
        size_t pos = ALPHABET_LOWER.find(c);
        if (pos != string::npos) {
            int x = (inv * ((int(pos) - b + m) % m)) % m;
            result += ALPHABET_LOWER[x];
        }
        else {
            pos = ALPHABET_UPPER.find(c);
            if (pos != string::npos) {
                int x = (inv * ((int(pos) - b + m) % m)) % m;
                result += ALPHABET_UPPER[x];
            }
            else {
                result += c;
            }
        }
    }
    return result;
}

int main(int argc, char* argv[]) {
    setlocale(LC_ALL, "");
    
    if (argc < 4) {
        cerr << "Usage: affine [encrypt|decrypt] a b" << endl;
        return 1;
    }
    
    string mode = argv[1];
    int a = stoi(argv[2]);
    int b = stoi(argv[3]);
    int m = ALPHABET_LOWER.size();
    
    if (gcd(a, m) != 1) {
        cerr << "ERROR: a must be coprime with " << m << endl;
        return 1;
    }
    
    string input, line;
    while (getline(cin, line)) {
        if (!input.empty()) input += '\n';
        input += line;
    }
    
    string output;
    if (mode == "encrypt") {
        output = encrypt(input, a, b);
    } else if (mode == "decrypt") {
        output = decrypt(input, a, b);
    } else {
        cerr << "ERROR: unknown mode" << endl;
        return 1;
    }
    
    cout << output;
    return 0;
}
