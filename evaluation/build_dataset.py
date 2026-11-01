"""Manually specified requirements, reference implementations and independent assertions.

These are project-owned coursework examples, not HumanEval/MBPP scores.
Running this script deterministically rebuilds the JSONL evaluation corpus.
"""
import json
from pathlib import Path

# name, requirements, trusted reference implementation, independent assertions
CASES = [
('sum_even', '实现 sum_even(nums)，返回整数列表中偶数之和，空列表返回 0。',
 'def sum_even(nums): return sum(x for x in nums if x % 2 == 0)',
 'assert sum_even([1,2,3,4]) == 6\nassert sum_even([]) == 0\nassert sum_even([-4,-3,2]) == -2'),
('is_palindrome', '实现 is_palindrome(text)，忽略大小写和非字母数字字符判断回文，空字符串为 True。',
 'def is_palindrome(text):\n s="".join(c.lower() for c in text if c.isalnum())\n return s == s[::-1]',
 'assert is_palindrome("A man, a plan, a canal: Panama")\nassert is_palindrome("")\nassert not is_palindrome("abc")'),
('factorial', '实现 factorial(n)，非负整数阶乘，0 返回 1，负数抛出 ValueError。',
 'def factorial(n):\n if n < 0: raise ValueError("negative")\n result=1\n for i in range(2,n+1): result*=i\n return result',
 'assert factorial(0)==1\nassert factorial(5)==120\nwith pytest.raises(ValueError): factorial(-1)'),
('binary_search', '实现 binary_search(nums,target)，升序无重复整数列表，返回匹配下标，不存在返回 -1。',
 'def binary_search(nums,target):\n lo,hi=0,len(nums)-1\n while lo<=hi:\n  mid=(lo+hi)//2\n  if nums[mid]==target: return mid\n  if nums[mid]<target: lo=mid+1\n  else: hi=mid-1\n return -1',
 'assert binary_search([1,3,5],5)==2\nassert binary_search([],1)==-1\nassert binary_search([1],1)==0\nassert binary_search([1,3],2)==-1'),
('unique_ordered', '实现 unique_ordered(items)，对可哈希元素去重并保留首次出现顺序。',
 'def unique_ordered(items): return list(dict.fromkeys(items))',
 'assert unique_ordered([3,1,3,2,1])==[3,1,2]\nassert unique_ordered([])==[]\nassert unique_ordered(["a","a","b"])==["a","b"]'),
('flatten', '实现 flatten(rows)，将二维列表展开一层，保留元素顺序，允许空子列表。',
 'def flatten(rows): return [x for row in rows for x in row]',
 'assert flatten([[1,2],[],[3]])==[1,2,3]\nassert flatten([])==[]\nassert flatten([[[]]])==[[]]'),
('word_counts', '实现 word_counts(text)，按空白分词并忽略大小写计数，标点保留在词中，返回字典。',
 'def word_counts(text):\n result={}\n for word in text.lower().split(): result[word]=result.get(word,0)+1\n return result',
 'assert word_counts("Hi hi Bye")=={"hi":2,"bye":1}\nassert word_counts("  ")=={}\nassert word_counts("a, a")=={"a,":1,"a":1}'),
('is_prime', '实现 is_prime(n)，判断整数是否为素数，小于 2 返回 False。',
 'def is_prime(n):\n if n<2: return False\n return all(n%d for d in range(2,int(n**0.5)+1))',
 'assert is_prime(2)\nassert is_prime(97)\nassert not is_prime(1)\nassert not is_prime(49)\nassert not is_prime(-7)'),
('fibonacci', '实现 fibonacci(n)，返回第 n 个斐波那契数，F0=0，F1=1，负数抛出 ValueError。',
 'def fibonacci(n):\n if n<0: raise ValueError("negative")\n a,b=0,1\n for _ in range(n): a,b=b,a+b\n return a',
 'assert fibonacci(0)==0\nassert fibonacci(1)==1\nassert fibonacci(10)==55\nwith pytest.raises(ValueError): fibonacci(-1)'),
('gcd', '实现 gcd(a,b)，返回两个整数的非负最大公约数，gcd(0,0)=0。',
 'def gcd(a,b):\n a,b=abs(a),abs(b)\n while b: a,b=b,a%b\n return a',
 'assert gcd(12,18)==6\nassert gcd(-12,18)==6\nassert gcd(0,0)==0\nassert gcd(0,7)==7'),
('merge_sorted', '实现 merge_sorted(a,b)，合并两个升序列表，保留重复值，不修改输入。',
 'def merge_sorted(a,b): return sorted(a+b)',
 'a=[1,3];b=[2,3]\nassert merge_sorted(a,b)==[1,2,3,3]\nassert a==[1,3] and b==[2,3]\nassert merge_sorted([],[])==[]'),
('rotate_right', '实现 rotate_right(items,k)，列表循环右移 k 位，负 k 表示左移，空列表返回空列表，不修改输入。',
 'def rotate_right(items,k):\n if not items: return []\n k%=len(items)\n return items[-k:]+items[:-k] if k else items[:]',
 'assert rotate_right([1,2,3],1)==[3,1,2]\nassert rotate_right([],3)==[]\nassert rotate_right([1,2,3],-1)==[2,3,1]\nassert rotate_right([1,2],4)==[1,2]'),
('chunked', '实现 chunked(items,size)，按正整数 size 分组，末组可不足，size<=0 抛出 ValueError。',
 'def chunked(items,size):\n if size<=0: raise ValueError("size")\n return [items[i:i+size] for i in range(0,len(items),size)]',
 'assert chunked([1,2,3,4,5],2)==[[1,2],[3,4],[5]]\nassert chunked([],2)==[]\nwith pytest.raises(ValueError): chunked([1],0)'),
('clamp', '实现 clamp(value,low,high)，将值限制在闭区间，low>high 时抛出 ValueError。',
 'def clamp(value,low,high):\n if low>high: raise ValueError("bounds")\n return max(low,min(high,value))',
 'assert clamp(2,0,5)==2\nassert clamp(-1,0,5)==0\nassert clamp(9,0,5)==5\nwith pytest.raises(ValueError): clamp(1,5,0)'),
('mean', '实现 mean(nums)，返回非空数值列表算术平均数，空列表抛出 ValueError。',
 'def mean(nums):\n if not nums: raise ValueError("empty")\n return sum(nums)/len(nums)',
 'assert mean([1,2,3])==2\nassert mean([-2,2])==0\nassert mean([2.5])==2.5\nwith pytest.raises(ValueError): mean([])'),
('median', '实现 median(nums)，返回中位数，偶数长度取中间两项平均，空列表抛出 ValueError，不修改输入。',
 'def median(nums):\n if not nums: raise ValueError("empty")\n s=sorted(nums);n=len(s)\n return s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2',
 'assert median([3,1,2])==2\nassert median([4,1,3,2])==2.5\nx=[3,1];median(x);assert x==[3,1]\nwith pytest.raises(ValueError): median([])'),
('balanced_brackets', '实现 balanced_brackets(text)，检查 () [] {} 括号是否正确嵌套，忽略其他字符，空串 True。',
 'def balanced_brackets(text):\n stack=[];pairs={")":"(","]":"[","}":"{"}\n for c in text:\n  if c in "([{": stack.append(c)\n  elif c in pairs:\n   if not stack or stack.pop()!=pairs[c]: return False\n return not stack',
 'assert balanced_brackets("a{[()]}")\nassert balanced_brackets("")\nassert not balanced_brackets("([)]")\nassert not balanced_brackets("(")'),
('two_sum', '实现 two_sum(nums,target)，返回首个遍历发现的两个不同元素下标元组，无解返回 None；从左到右扫描，优先匹配已见元素。',
 'def two_sum(nums,target):\n seen={}\n for i,x in enumerate(nums):\n  if target-x in seen: return (seen[target-x],i)\n  if x not in seen: seen[x]=i\n return None',
 'assert two_sum([2,7,11],9)==(0,1)\nassert two_sum([3,3],6)==(0,1)\nassert two_sum([1],2) is None\nassert two_sum([],0) is None'),
('longest_common_prefix', '实现 longest_common_prefix(words)，返回字符串列表的最长公共前缀，空列表返回空字符串。',
 'def longest_common_prefix(words):\n if not words: return ""\n prefix=words[0]\n for word in words[1:]:\n  while not word.startswith(prefix): prefix=prefix[:-1]\n return prefix',
 'assert longest_common_prefix(["flower","flow","flight"])=="fl"\nassert longest_common_prefix([])==""\nassert longest_common_prefix(["a",""])==""\nassert longest_common_prefix(["abc"])=="abc"'),
('run_length_encode', '实现 run_length_encode(text)，返回连续字符的 (字符,次数) 元组列表，空字符串返回空列表。',
 'def run_length_encode(text):\n result=[]\n for c in text:\n  if result and result[-1][0]==c: result[-1]=(c,result[-1][1]+1)\n  else: result.append((c,1))\n return result',
 'assert run_length_encode("aaabbc")==[("a",3),("b",2),("c",1)]\nassert run_length_encode("")==[]\nassert run_length_encode("aba")==[("a",1),("b",1),("a",1)]'),
('transpose', '实现 transpose(matrix)，对矩形二维列表转置，空列表返回空列表，行长度不一致抛出 ValueError。',
 'def transpose(matrix):\n if not matrix: return []\n if any(len(row)!=len(matrix[0]) for row in matrix): raise ValueError("ragged")\n return [list(row) for row in zip(*matrix)]',
 'assert transpose([[1,2],[3,4]])==[[1,3],[2,4]]\nassert transpose([])==[]\nassert transpose([[],[]])==[]\nwith pytest.raises(ValueError): transpose([[1],[2,3]])'),
('merge_intervals', '实现 merge_intervals(intervals)，合并闭区间，端点相接也合并，返回按左端点排序的列表，不修改输入。输入区间均合法。',
 'def merge_intervals(intervals):\n result=[]\n for a,b in sorted(intervals):\n  if result and a<=result[-1][1]: result[-1][1]=max(result[-1][1],b)\n  else: result.append([a,b])\n return result',
 'assert merge_intervals([[1,3],[2,5],[7,9]])==[[1,5],[7,9]]\nassert merge_intervals([[2,3],[1,2]])==[[1,3]]\nassert merge_intervals([])==[]\nx=[[1,3],[2,4]];merge_intervals(x);assert x==[[1,3],[2,4]]'),
('is_anagram', '实现 is_anagram(a,b)，忽略大小写与空白，其他字符参与比较，判断是否字符重排。',
 'def is_anagram(a,b):\n clean=lambda s:sorted(c.lower() for c in s if not c.isspace())\n return clean(a)==clean(b)',
 'assert is_anagram("Dormitory","Dirty room")\nassert is_anagram("","")\nassert not is_anagram("aa","a")\nassert not is_anagram("a!","a")'),
('count_bits', '实现 count_bits(n)，返回非负整数二进制中 1 的数量，负数抛出 ValueError。',
 'def count_bits(n):\n if n<0: raise ValueError("negative")\n return n.bit_count()',
 'assert count_bits(0)==0\nassert count_bits(7)==3\nassert count_bits(1024)==1\nwith pytest.raises(ValueError): count_bits(-1)'),
('safe_divide', '实现 safe_divide(a,b)，正常返回 a/b，除数为 0 返回 None。',
 'def safe_divide(a,b): return a/b if b!=0 else None',
 'assert safe_divide(6,3)==2\nassert safe_divide(0,3)==0\nassert safe_divide(1,0) is None\nassert safe_divide(-3,2)==-1.5'),
('slugify', '实现 slugify(text)，仅保留 ASCII 小写字母与数字，其他字符连续段替换为一个短横线，去除首尾短横线。',
 'import re\ndef slugify(text): return re.sub(r"[^a-z0-9]+","-",text.lower()).strip("-")',
 'assert slugify(" Hello, World! ")=="hello-world"\nassert slugify("")==""\nassert slugify("a___b")=="a-b"\nassert slugify("中文")==""'),
('first_unique', '实现 first_unique(text)，返回第一个只出现一次的字符下标，无则返回 -1，区分大小写。',
 'from collections import Counter\ndef first_unique(text):\n counts=Counter(text)\n return next((i for i,c in enumerate(text) if counts[c]==1),-1)',
 'assert first_unique("leetcode")==0\nassert first_unique("aabbc")==4\nassert first_unique("aabb")==-1\nassert first_unique("")==-1'),
('intersection_ordered', '实现 intersection_ordered(a,b)，返回交集去重列表，按 a 的首次出现顺序，元素可哈希。',
 'def intersection_ordered(a,b):\n allowed=set(b)\n return list(dict.fromkeys(x for x in a if x in allowed))',
 'assert intersection_ordered([3,1,2,3],[2,3])==[3,2]\nassert intersection_ordered([],[])==[]\nassert intersection_ordered([1,1],[1])==[1]'),
('parse_ints', '实现 parse_ints(text)，逗号分隔整数，忽略各段首尾空白和空段，任何非空段非法则抛出 ValueError。',
 'def parse_ints(text): return [int(x.strip()) for x in text.split(",") if x.strip()]',
 'assert parse_ints("1, -2,3")==[1,-2,3]\nassert parse_ints(" , ,")==[]\nassert parse_ints("1,,2")==[1,2]\nwith pytest.raises(ValueError): parse_ints("1,x")'),
('moving_average', '实现 moving_average(nums,window)，返回所有完整窗口的平均值，window<=0 抛出 ValueError，窗口超过列表长度返回空列表。',
 'def moving_average(nums,window):\n if window<=0: raise ValueError("window")\n return [sum(nums[i:i+window])/window for i in range(len(nums)-window+1)]',
 'assert moving_average([1,2,3,4],2)==[1.5,2.5,3.5]\nassert moving_average([],2)==[]\nassert moving_average([1],3)==[]\nwith pytest.raises(ValueError): moving_average([1],0)'),
]

BUGS = [
 'def sum_even(nums): return sum(x for x in nums if x % 2 != 0)',
 'def is_palindrome(text): return text == text[::-1]',
 'def factorial(n):\n result=0\n for i in range(1,n+1): result*=i\n return result',
 'def binary_search(nums,target):\n for i in range(len(nums)-1):\n  if nums[i]==target: return i\n return -1',
 'def unique_ordered(items): return sorted(set(items))',
 'def flatten(rows): return rows[0]',
 'def word_counts(text):\n result={}\n for w in text.split(): result[w]=1\n return result',
 'def is_prime(n): return all(n%d for d in range(2,n))',
 'def fibonacci(n):\n if n<0: raise ValueError()\n a,b=0,1\n for _ in range(n+1): a,b=b,a+b\n return a',
 'def gcd(a,b)\n while b: a,b=b,a%b\n return a',
 'def merge_sorted(a,b):\n a.extend(b)\n a.sort()\n return a',
 'def rotate_right(items,k):\n k%=len(items)\n return items[k:]+items[:k]',
 'def chunked(items,size): return [items[i:i+size] for i in range(0,len(items)-size+1,size)]',
 'def clamp(value,low,high): return min(low,max(high,value))',
 'def mean(nums): return sum(nums)//len(nums)',
]


def records():
    rows = []
    for i,(name,requirement,reference,assertions) in enumerate(CASES):
        tests = f'import pytest\nfrom solution import {name}\n\ndef test_contract():\n' + '\n'.join('    '+line for line in assertions.splitlines()) + '\n'
        common = dict(language='python',requirement=requirement,reference=reference+'\n',tests=tests,
            context_files=[{'path':'CONVENTIONS.md','content':'项目使用 Python 标准库，函数保持无副作用。保留需求指定的函数名和参数。错误采用 ValueError。'}])
        rows.append(dict(id=f'gen-{i+1:02}',kind='generate',**common))
        if i < len(BUGS): rows.append(dict(id=f'fix-{i+1:02}',kind='fix',buggy=BUGS[i]+'\n',**common))
    return rows


if __name__ == '__main__':
    destination = Path(__file__).with_name('cases.jsonl')
    destination.write_text('\n'.join(json.dumps(row,ensure_ascii=False) for row in records())+'\n',encoding='utf-8')
    print(f'Wrote {len(records())} cases: 30 generation + 15 repair')
