"""
Merge Sort and Quick Sort implemented from first principles.
Used to sort banking transaction records by amount or timestamp.
"""
from typing import Any, Callable, List, Tuple


def merge_sort(
    items: List[Any],
    key: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], int]:
    """
    Merge Sort algorithm implemented from first principles.
    Time Complexity: O(N log N) in all cases (Best, Average, Worst).
    Space Complexity: O(N) auxiliary space.
    Stable sort.
    Returns: (sorted_list, comparison_count)
    """
    if len(items) <= 1:
        return list(items), 0

    comparison_count = 0

    def _merge_sort_recursive(arr: List[Any]) -> Tuple[List[Any], int]:
        nonlocal comparison_count
        if len(arr) <= 1:
            return arr, 0

        mid = len(arr) // 2
        left, _ = _merge_sort_recursive(arr[:mid])
        right, _ = _merge_sort_recursive(arr[mid:])

        merged = []
        i = j = 0

        while i < len(left) and j < len(right):
            comparison_count += 1
            left_val = key(left[i])
            right_val = key(right[j])

            condition = (left_val >= right_val) if reverse else (left_val <= right_val)
            if condition:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        while i < len(left):
            merged.append(left[i])
            i += 1

        while j < len(right):
            merged.append(right[j])
            j += 1

        return merged, comparison_count

    sorted_arr, _ = _merge_sort_recursive(list(items))
    return sorted_arr, comparison_count


def quick_sort(
    items: List[Any],
    key: Callable[[Any], Any] = lambda x: x,
    reverse: bool = False
) -> Tuple[List[Any], int]:
    """
    Quick Sort algorithm implemented from first principles.
    Uses median-of-three pivot selection to prevent O(N^2) degradation on sorted data.
    Time Complexity: O(N log N) Average, O(N^2) Worst case.
    Space Complexity: O(log N) stack space.
    Returns: (sorted_list, comparison_count)
    """
    arr = list(items)
    comparison_count = 0

    def _median_of_three(low: int, mid: int, high: int) -> int:
        nonlocal comparison_count
        a, b, c = key(arr[low]), key(arr[mid]), key(arr[high])
        comparison_count += 2
        if (a <= b <= c) or (c <= b <= a):
            return mid
        elif (b <= a <= c) or (c <= a <= b):
            return low
        else:
            return high

    def _partition(low: int, high: int) -> int:
        nonlocal comparison_count
        # Median of three pivot selection
        mid = (low + high) // 2
        pivot_idx = _median_of_three(low, mid, high)
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]

        pivot_val = key(arr[high])
        i = low - 1

        for j in range(low, high):
            comparison_count += 1
            curr_val = key(arr[j])
            condition = (curr_val >= pivot_val) if reverse else (curr_val <= pivot_val)
            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def _quick_sort_recursive(low: int, high: int):
        if low < high:
            pi = _partition(low, high)
            _quick_sort_recursive(low, pi - 1)
            _quick_sort_recursive(pi + 1, high)

    if len(arr) > 1:
        _quick_sort_recursive(0, len(arr) - 1)

    return arr, comparison_count
