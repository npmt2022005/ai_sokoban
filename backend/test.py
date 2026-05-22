"""
Thuật toán Hungarian (Kuhn-Munkres)
=====================================
Tìm phân công tối ưu (chi phí nhỏ nhất) giữa n tác nhân và n công việc.
Input:  cost_matrix[i][j] = chi phí gán tác nhân i cho công việc j
Output: tổng chi phí nhỏ nhất + danh sách phân công [(i, j), ...]
"""

INF = float('inf')





# ── Ứng dụng trong Sokoban: boxes → targets ───────────────────────────────────

def manhattan(a: tuple, b: tuple) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def min_matching_cost(boxes: list[tuple], targets: list[tuple]) -> int:
    """
    Tính tổng khoảng cách Manhattan nhỏ nhất khi gán mỗi box 1 target.
    Dùng làm heuristic admissible cho A*.
    """
    n = len(boxes)
    assert n == len(targets), "Số hộp phải bằng số target"
    cost_matrix = [
        [manhattan(boxes[i], targets[j]) for j in range(n)]
        for i in range(n)
    ]
    min_cost, _ = hungarian(cost_matrix)
    return min_cost


# ══════════════════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════════════════

def run_tests():
    import itertools

    def brute_force(cm):
        n = len(cm)
        best = INF
        for perm in itertools.permutations(range(n)):
            best = min(best, sum(cm[i][perm[i]] for i in range(n)))
        return best

    cases = [
        {
            "name": "3×3 cơ bản",
            "matrix": [[4,1,3],[2,0,5],[3,2,2]],
        },
        {
            "name": "4×4 cổ điển",
            "matrix": [[9,2,7,8],[6,4,3,7],[5,8,1,8],[7,6,9,4]],
        },
        {
            "name": "1×1",
            "matrix": [[7]],
        },
        {
            "name": "2×2",
            "matrix": [[1,2],[3,4]],
        },
        {
            "name": "3×3 đồng nhất",
            "matrix": [[3,3,3],[3,3,3],[3,3,3]],
        },
        {
            "name": "5×5 ngẫu nhiên",
            "matrix": [
                [12, 9,27, 10, 23],
                [7,  13, 3,  2, 18],
                [4,  21, 14,  8, 5 ],
                [17, 6,  11, 19, 1 ],
                [25, 2,  16,  7, 20],
            ],
        },
    ]

    print("=" * 55)
    print("TEST THUẬT TOÁN HUNGARIAN")
    print("=" * 55)

    passed = 0
    for i, tc in enumerate(cases, 1):
        expected = brute_force(tc["matrix"])
        cost, assign = hungarian(tc["matrix"])
        ok = cost == expected
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"\n{status} | Test {i}: {tc['name']}")
        for row in tc["matrix"]:
            print(f"  {row}")
        print(f"  Phân công : {assign}")
        print(f"  Chi phí   : {cost}  (expected: {expected})")
        if ok:
            passed += 1

    # ── Test Sokoban ──────────────────────────────────────────────────────
    boxes   = [(1,1),(3,4),(5,2)]
    targets = [(1,4),(3,1),(5,5)]
    cost = min_matching_cost(boxes, targets)
    cm = [[manhattan(boxes[i], targets[j]) for j in range(3)] for i in range(3)]
    expected = brute_force(cm)
    ok = cost == expected
    status = "✅ PASS" if ok else "❌ FAIL"
    print(f"\n{status} | Test Sokoban heuristic")
    print(f"  Boxes  : {boxes}")
    print(f"  Targets: {targets}")
    print(f"  Chi phí Manhattan tối ưu: {cost}  (expected: {expected})")
    if ok:
        passed += 1

    total = len(cases) + 1
    print(f"\n{'─'*55}")
    print(f"Kết quả: {passed}/{total} passed", end="")
    print("  ✅ Tất cả pass!" if passed == total else f"  ❌ {total-passed} failed")


if __name__ == "__main__":
    run_tests()