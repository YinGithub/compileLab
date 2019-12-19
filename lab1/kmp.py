def get_fail_func(str):
     f = [0] * len(str)
     j = 0 
     for i in range(1,len(str)):
         while(j> 0 and str[i] != str[j]):
             j = f[j-1]
         if str[i] == str[j]:
             j = j +1
             f[i] = j
         else:
            f[i] = 0
     return f

# kmp compare 
def KMP_compare(src_str,pattern):
    f = get_fail_func(pattern)
    j = 0
    for i in range(0,len(src_str)):
        while(j>0 and src_str[i] != pattern[j]):
            j = f[j-1]
        if src_str[i] == pattern[j]:
            j = j+1
            if j == len(pattern):
                return i-(j-1)
    return -1

print KMP_compare("ababaa","aa")

