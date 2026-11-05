#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import time
from functools import cmp_to_key

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Сложность: O(n^2) в среднем и худшем,
    O(n) в лучшем (упорядоченный вход, один проход без обменов).

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    a = list(a)
    comparisons = swaps = 0
    for i in range(len(a) - 1):
        swapped = False
        for j in range(len(a) - 1 - i):  
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:  
            break
    return a, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Сложность: O(n) в лучшем случае (упорядоченный вход),
    O(n^2) в среднем и худшем (число сдвигов = числу инверсий)."""
    a = list(a)
    comparisons = moves = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] <= key: 
                break
            a[j + 1] = a[j] 
            moves += 1
            j -= 1
        a[j + 1] = key
    return a, comparisons, moves


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Сложность: Θ(n^2) на любом входе, потому что поиск
    минимума всегда просматривает весь остаток: ровно n(n-1)/2 сравнений."""
    a = list(a)
    comparisons = swaps = 0
    for i in range(len(a) - 1):
        m = i  # индекс минимума в a[i:]
        for j in range(i + 1, len(a)):
            comparisons += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            swaps += 1
    return a, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем O(n log n), в худшем случае O(n^2). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    a = list(a)

    def sort(lo: int, hi: int) -> None: 
        if hi - lo < 2: 
            return
        p = rng.randrange(lo, hi)  
        a[p], a[hi - 1] = a[hi - 1], a[p]  
        pivot = a[hi - 1]
        i = lo  # граница: в a[lo:i] все элементы меньше опорного
        for j in range(lo, hi - 1):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi - 1] = a[hi - 1], a[i]  # опорный встаёт на своё место
        sort(lo, i)
        sort(i + 1, hi)

    sort(0, len(a))
    return a


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    # Обёртка, сравнивающая пары только по ключу p[0]
    by_key = cmp_to_key(lambda x, y: x[0] - y[0])
    small = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    big = [(random.randrange(4), i) for i in range(40)]  
    sorts = {
        "bubble_sort": lambda a: bubble_sort(a)[0],
        "insertion_sort": lambda a: insertion_sort(a)[0],
        "selection_sort": lambda a: selection_sort(a)[0],
        "quick_sort": lambda a: quick_sort(a, random.Random(1)),
    }
    for name, fn in sorts.items():
        res = [w.obj for w in fn([by_key(p) for p in small])]
        res_big = [w.obj for w in fn([by_key(p) for p in big])]
        # sorted() стабилен, поэтому его порядок меток — эталон
        stable = res_big == sorted(big, key=lambda p: p[0])
        print(f"{name:<15} {res} -> {'стабильна' if stable else 'НЕстабильна'}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    times = {}  # (алгоритм, класс входа) -> [(n, время), ...]
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                times.setdefault((name, cls), []).append((n, t))
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")

    # Наклон прямой на log-log графике: t ~ n^k, k≈2 -> O(n^2), k≈1 -> n log n
    print("\nНаклоны k (t ~ n^k):")
    for (name, cls), pts in times.items():
        xs = [math.log(n) for n, _ in pts]
        ys = [math.log(t) for _, t in pts]
        print(f"  {name:<15} {cls:<13} k={statistics.linear_regression(xs, ys).slope:.2f}")

    # Счётчики сравнений / обменов на небольших n
    print("\nСчётчики (сравнения/обмены):")
    for n in SIZES_QUADRATIC[:3]:
        for cls, data in make_inputs(n, seed).items():
            row = [f"{f.__name__}={f(data)[1]}/{f(data)[2]}"
                   for f in (bubble_sort, insertion_sort, selection_sort)]
            print(f"  n={n:>5} {cls:<13}", "  ".join(row))

    # Log-log графики: по одному окну на класс входа
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    for ax, cls in zip(axes, ("упорядоченный", "случайный", "обратный")):
        for (name, c), pts in times.items():
            if c == cls:
                ax.loglog(*zip(*pts), marker="o", label=name)
        ax.set_title(cls)
        ax.set_xlabel("n")
    axes[0].set_ylabel("время, с")
    axes[0].legend()
    fig.savefig(f"lab03_loglog_seed{seed}.png", dpi=150)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()