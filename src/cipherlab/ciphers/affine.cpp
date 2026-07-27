#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <clocale>
#include <cmath>

using namespace std;

// Русский алфавит с ё (33 буквы)
const vector<string> RU_ALPHABET_LOWER = {
    "а","б","в","г","д","е","ё","ж","з","и","й","к","л","м",
    "н","о","п","р","с","т","у","ф","х","ц","ч","ш","щ",
    "ъ","ы","ь","э","ю","я"
};

const vector<string> RU_ALPHABET_UPPER = {
    "А","Б","В","Г","Д","Е","Ё","Ж","З","И","Й","К","Л","М",
    "Н","О","П","Р","С","Т","У","Ф","Х","Ц","Ч","Ш","Щ",
    "Ъ","Ы","Ь","Э","Ю","Я"
};

// Английский алфавит (26 букв)
const vector<string> EN_ALPHABET_LOWER = {
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z"
};

const vector<string> EN_ALPHABET_UPPER = {
    "A","B","C","D","E","F","G","H","I","J","K","L","M",
    "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"
};

int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int modInverse(int a, int m) {
    a = ((a % m) + m) % m;
    for (int i = 1; i < m; i++) {
        if ((a * i) % m == 1)
            return i;
    }
    return -1;
}

// Разбивает UTF-8 строку на вектор символов
vector<string> utf8Split(const string& str) {
    vector<string> result;
    size_t i = 0;
    while (i < str.size()) {
        size_t len = 1;
        unsigned char c = str[i];
        if (c >= 0x80) {
            if ((c & 0xE0) == 0xC0) len = 2;
            else if ((c & 0xF0) == 0xE0) len = 3;
            else if ((c & 0xF8) == 0xF0) len = 4;
        }
        result.push_back(str.substr(i, len));
        i += len;
    }
    return result;
}

// Склеивает вектор символов в строку UTF-8
string utf8Join(const vector<string>& chars) {
    string result;
    for (const auto& ch : chars) {
        result += ch;
    }
    return result;
}

// Находит позицию символа в алфавите
int findInAlphabet(const string& ch, const vector<string>& alphabet) {
    for (size_t i = 0; i < alphabet.size(); i++) {
        if (alphabet[i] == ch) {
            return i;
        }
    }
    return -1;
}

// Определяет язык по первому символу
string detectLanguage(const string& text) {
    if (text.empty()) return "ru";
    
    vector<string> chars = utf8Split(text);
    for (const string& ch : chars) {
        // Проверяем русские буквы
        if (findInAlphabet(ch, RU_ALPHABET_LOWER) != -1 || 
            findInAlphabet(ch, RU_ALPHABET_UPPER) != -1) {
            return "ru";
        }
        // Проверяем английские буквы
        if (findInAlphabet(ch, EN_ALPHABET_LOWER) != -1 || 
            findInAlphabet(ch, EN_ALPHABET_UPPER) != -1) {
            return "en";
        }
    }
    return "ru"; // по умолчанию русский
}

string encrypt(const string& text, int a, int b, const string& lang) {
    vector<string> chars = utf8Split(text);
    string result;
    
    const vector<string>* lower_alphabet;
    const vector<string>* upper_alphabet;
    int m;
    
    if (lang == "en") {
        lower_alphabet = &EN_ALPHABET_LOWER;
        upper_alphabet = &EN_ALPHABET_UPPER;
        m = EN_ALPHABET_LOWER.size();
    } else {
        lower_alphabet = &RU_ALPHABET_LOWER;
        upper_alphabet = &RU_ALPHABET_UPPER;
        m = RU_ALPHABET_LOWER.size();
    }
    
    for (const string& ch : chars) {
        int pos = findInAlphabet(ch, *lower_alphabet);
        if (pos != -1) {
            int x = (a * pos + b) % m;
            result += (*lower_alphabet)[x];
        }
        else {
            pos = findInAlphabet(ch, *upper_alphabet);
            if (pos != -1) {
                int x = (a * pos + b) % m;
                result += (*upper_alphabet)[x];
            }
            else {
                result += ch;
            }
        }
    }
    return result;
}

string decrypt(const string& text, int a, int b, const string& lang) {
    vector<string> chars = utf8Split(text);
    string result;
    
    const vector<string>* lower_alphabet;
    const vector<string>* upper_alphabet;
    int m;
    
    if (lang == "en") {
        lower_alphabet = &EN_ALPHABET_LOWER;
        upper_alphabet = &EN_ALPHABET_UPPER;
        m = EN_ALPHABET_LOWER.size();
    } else {
        lower_alphabet = &RU_ALPHABET_LOWER;
        upper_alphabet = &RU_ALPHABET_UPPER;
        m = RU_ALPHABET_LOWER.size();
    }
    
    int inv = modInverse(a, m);
    if (inv == -1) {
        return "ERROR: no modular inverse for a=" + to_string(a) + " mod " + to_string(m);
    }
    
    for (const string& ch : chars) {
        int pos = findInAlphabet(ch, *lower_alphabet);
        if (pos != -1) {
            int x = (inv * ((pos - b + m) % m)) % m;
            result += (*lower_alphabet)[x];
        }
        else {
            pos = findInAlphabet(ch, *upper_alphabet);
            if (pos != -1) {
                int x = (inv * ((pos - b + m) % m)) % m;
                result += (*upper_alphabet)[x];
            }
            else {
                result += ch;
            }
        }
    }
    return result;
}

int main(int argc, char* argv[]) {
    setlocale(LC_ALL, "en_US.UTF-8");
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    if (argc < 4) {
        cerr << "Usage: affine [encrypt|decrypt] a b [lang]" << endl;
        cerr << "  lang: ru (default) or en" << endl;
        cerr << "Example: affine encrypt 5 8 ru" << endl;
        cerr << "Example: affine encrypt 3 7 en" << endl;
        return 1;
    }
    
    string mode = argv[1];
    int a = stoi(argv[2]);
    int b = stoi(argv[3]);
    string lang = "ru";
    
    if (argc >= 5) {
        lang = argv[4];
        if (lang != "ru" && lang != "en") {
            cerr << "ERROR: lang must be 'ru' or 'en'" << endl;
            return 1;
        }
    }
    
    int m = (lang == "en") ? 26 : 33;
    
    if (gcd(a, m) != 1) {
        cerr << "ERROR: a=" << a << " must be coprime with " << m << endl;
        return 1;
    }
    
    // Читаем весь stdin как UTF-8
    string input;
    string line;
    while (getline(cin, line)) {
        if (!input.empty()) input += '\n';
        input += line;
    }
    
    // Если язык не указан, определяем автоматически
    if (argc < 5) {
        lang = detectLanguage(input);
    }
    
    string output;
    if (mode == "encrypt") {
        output = encrypt(input, a, b, lang);
    } else if (mode == "decrypt") {
        output = decrypt(input, a, b, lang);
    } else {
        cerr << "ERROR: unknown mode: " << mode << endl;
        return 1;
    }
    
    cout << output;
    return 0;
}
