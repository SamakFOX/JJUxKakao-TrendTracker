def dType(x):
    return type(x).__name__

age = 19;
ages = [10, 20, 30, 18.5, '안녕'];

# 제한연령 체크
for check in ages :
    if not isinstance(check, int) : 
        print(f"Type MissMatch -> {check}({dType(check)})")
        continue
    print(
        f"제한연령인 {age}보다 "
        f"{abs(age - check)} 만큼 "
        f"{'작습니다' if check < age else '큽니다'}"
    )
