import random
import re
import string
import math
import os
from collections import Counter


DEFAULT_CORPUS = """
Here is a long piece written entirely in English, capturing the rhythm of quiet introspection, late-night creative energy, and the journey of youth:

In the quiet hours of the night, when the rest of the world has finally grown still and the ambient hum of the city fades into a distant murmur, there exists a very particular kind of solitude. It is not a lonely or isolating kind of silence; rather, it is a spacious, breathable canvas where the mind can finally wander without constraint. During these hours, the boundaries between logic and imagination begin to dissolve. The glowing lines of code, the unfinished paragraphs of an essay, and the lingering echoes of a familiar melody all start to weave themselves together into a coherent narrative of what it means to be young, restless, and relentlessly searching for meaning.

Growing up in an era defined by perpetual motion and digital noise, we often find ourselves caught in a relentless cycle of productivity. We build systems, configure networks, optimize routines, and chase after ambitious academic and professional milestones. Yet, beneath the mechanics of daily survival and technical problem-solving lies a deeper, quieter hunger—a desire to capture the transient beauty of human experience. Whether it is through the melancholic chords of an indie record, the intricate world-building of a creative script, or the simple act of putting pen to paper to reflect on a fleeting emotion, art and technology are not opposing forces. Instead, they are two sides of the same coin, both born from the fundamental urge to create order out of chaos, to leave a mark, and to say: I was here, and I felt deeply.

There are moments when the weight of uncertainty feels heavy on our shoulders. We question the paths we have chosen, the projects that demand our endless patience, and the future that remains stubbornly unwritten. We stare at blank screens, battling stubborn bugs in our software or struggling to find the exact vocabulary to describe a subtle shift in perspective. But it is precisely within these struggles that personal growth takes root. The late nights spent debugging a virtual machine, the endless revisions of a written piece, and the painstaking assembly of a hardware prototype are testaments to a stubborn perseverance. We do not just build things because we have to; we build them because the act of creation is a form of self-discovery.

As we navigate the complexities of university life and the early chapters of adulthood, we are constantly learning how to balance the analytical with the poetic. We study the precise protocols of data transmission while simultaneously trying to decode the erratic signals of our own hearts. We learn that it is entirely acceptable to feel lost, as long as we keep moving forward, armed with curiosity, a cup of coffee, and a playlist that understands our moods better than anyone else. The journey is messy, unpredictable, and rarely follows a straight line, but that is precisely what makes it worth documenting. In the end, the stories we tell, the code we compile, and the memories we preserve are the true architecture of our youth—imperfect, enduring, and entirely our own.
"""

class NgramScore:
    def __init__(self, text, n=3):
        self.n = n
        self.ngrams = {}
        # Tien xu ly: loai bo cac ky tu khong phai chu cai
        text = re.sub(r'[^A-Z]', '', text.upper())
        
        # Dem tan suat cac N-gram
        for i in range(len(text) - n + 1):
            gram = text[i:i+n]
            self.ngrams[gram] = self.ngrams.get(gram, 0) + 1
            
        # Tinh log co so 10 cua xac suat de tranh underflow khi cong don
        self.total = sum(self.ngrams.values())
        for key in self.ngrams:
            self.ngrams[key] = math.log10(float(self.ngrams[key]) / self.total)
        # Diem phat cuc thap cho nhung N-gram khong ton tai trong tu dien huan luyen
        self.floor = math.log10(0.01 / self.total)

    def score(self, text):
        score = 0
        text = re.sub(r'[^A-Z]', '', text.upper())
        for i in range(len(text) - self.n + 1):
            gram = text[i:i+self.n]
            if gram in self.ngrams:
                score += self.ngrams[gram]
            else:
                score += self.floor
        return score

def decrypt(ciphertext, key):
    #Giai ma van ban voi mot khoa cu the
    cipher_alphabet = string.ascii_uppercase
    trans = str.maketrans(cipher_alphabet, ''.join(key))
    upper_cipher = ciphertext.upper()
    decrypted = upper_cipher.translate(trans)
    
    # Khoi phuc dinh dang in hoa/in thuong
    result = []
    for c_orig, c_dec in zip(ciphertext, decrypted):
        if c_orig.islower():
            result.append(c_dec.lower())
        else:
            result.append(c_dec)
    return ''.join(result)

def solve_substitution(ciphertext, scorer, restarts=10):
    """Thuat toan Hill Climbing de tim khoa giai ma tot nhat"""
    alphabet = list(string.ascii_uppercase)
    best_overall_key = alphabet[:]
    best_overall_score = -float('inf')

    print("\n--- Bat dau qua trinh Hill Climbing ---")
    for i in range(restarts):
        # Khoi tao mot khoa ngau nhien
        current_key = alphabet[:]
        random.shuffle(current_key)
        current_score = scorer.score(decrypt(ciphertext, current_key))
        
        count = 0
        # Thay doi khoa lien tuc cho den khi khong tim thay ket qua tot hon sau 1000 vong lap
        while count < 1000:
            child_key = current_key[:]
            # Doi cho ngau nhien 2 ky tu trong khoa
            a, b = random.sample(range(26), 2)
            child_key[a], child_key[b] = child_key[b], child_key[a]
            
            child_score = scorer.score(decrypt(ciphertext, child_key))
            
            # Neu khoa moi cho diem cao hon (ban ro giong ngon ngu tu nhien hon), giu lai khoa do
            if child_score > current_score:
                current_key = child_key
                current_score = child_score
                count = 0 # Reset bo dem
            else:
                count += 1
                
        # 3. Luu lai khoa tot nhat sau toan bo qua trinh
        if current_score > best_overall_score:
            best_overall_score = current_score
            best_overall_key = current_key[:]
        print(f"  Vong lap {i+1}/{restarts}: Diem N-gram = {current_score:.2f} | Mau thu tot nhat:\n{decrypt(ciphertext, current_key)}\n" + "-"*40)
    return ''.join(best_overall_key), best_overall_score

def main():
    print("=== CHUONG TRINH GIAI MA MONO-ALPHABETIC SUBSTITUTION ===")
    
    # Lay van ban huan luyen tu file corpus.txt neu co, neu khong thi dung mau mac dinh
    corpus = DEFAULT_CORPUS
    if os.path.exists('corpus.txt'):
        with open('corpus.txt', 'r', encoding='utf-8') as f:
            corpus = f.read()
        print("[+] Da tai mo hinh ngon ngu tu 'corpus.txt'.")
    else:
        print("[!] Dang su dung mo hinh ngon ngu mac dinh (khuyen dung file corpus.txt lon hon de tang do chinh xac).")
        
    scorer = NgramScore(corpus, n=3)

    choice = input("\nBan muon nhap ciphertext tu dau?\n1. Nhap tu ban phim (Ho tro nhieu dong)\n2. Doc tu file\nLua chon (1/2): ").strip()
    
    ciphertext = ""
    if choice == '2':
        filename = input("Nhap ten file (VD: ciphertext.txt): ").strip()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                ciphertext = f.read()
        except FileNotFoundError:
            print("Khong tim thay file! Thoat chuong trinh.")
            return
    else:
        print("Nhap ciphertext (Dan nguyen doan van ban dai vao day).")
        print("Luu y: Khi da paste xong, go chu 'END' o mot dong moi va nhan Enter de bat dau giai ma:")
        lines = []
        while True:
            try:
                line = input()
                # Kiem tra neu nguoi dung go END thi dung viec doc du lieu
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        ciphertext = '\n'.join(lines)

    if not ciphertext.strip():
        print("Khong co du lieu dau vao!")
        return

    # Chay 20 vong lap random restart de tim ra dinh tot nhat
    best_key, best_score = solve_substitution(ciphertext, scorer, restarts=20)
    best_plaintext = decrypt(ciphertext, best_key)

    print("\n" + "="*50)
    print("KET QUA TOT NHAT:")
    print("="*50)
    print(f"Key thay the (A-Z): {best_key}")
    print(f"Diem so (Score):    {best_score:.2f}")
    print("-" * 50)
    print(best_plaintext)
    print("=" * 50)

if __name__ == "__main__":
    main()