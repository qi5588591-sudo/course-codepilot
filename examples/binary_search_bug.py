"""Demonstration input: intentionally misses the final element."""
def binary_search(nums, target):
    for i in range(len(nums) - 1):
        if nums[i] == target:
            return i
    return -1
