"""Метод Касиски: оценка длины ключа Виженера по повторяющимся подстрокам."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations


def kasiski_examination(
    ciphertext: str, min_seq_len: int = 3, max_key_len: int = 20, min_support: int = 2
) -> list[int]:
    """Возвращает кандидатов длины ключа, ранжированных по числу подтверждений.

    Подтверждением считается количество РАЗНЫХ значений расстояния, делящихся
    на длину — не количество пар повторов. Одно случайное совпадение
    триграммы даёт одно расстояние, а значит "голос" ровно за один набор
    делителей: этого недостаточно, чтобы доверять такому делителю. Один
    протяжённый повтор куска текста (например, если во входе случайно
    продублирована фраза) — тоже всего одно расстояние, просто с кучей
    перекрывающихся триграмм внутри, дающих много ПАР с одним и тем же
    расстоянием; будь подтверждением число пар, а не число различных
    расстояний, такой повтор ложно выглядел бы как сильное свидетельство
    периодичности ключа. Настоящий периодический ключ Виженера, напротив,
    даёт совпадения на РАЗНЫХ расстояниях (в разных местах текста), все —
    кратные истинной длине ключа, поэтому только различные расстояния
    считаются независимым голосом.
    """
    positions: dict[str, list[int]] = defaultdict(list)
    for i in range(len(ciphertext) - min_seq_len + 1):
        seq = ciphertext[i:i + min_seq_len]
        positions[seq].append(i)

    distances = set()
    for seq, idxs in positions.items():
        if len(idxs) > 1:
            for a, b in combinations(idxs, 2):
                distances.add(b - a)

    factor_counts: dict[int, int] = defaultdict(int)
    for d in distances:
        for f in range(2, max_key_len + 1):
            if d % f == 0:
                factor_counts[f] += 1

    candidates = [f for f, count in factor_counts.items() if count >= min_support]
    return sorted(candidates, key=factor_counts.get, reverse=True)
