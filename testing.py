import re
input_num = '1234' 
pattern = '^[0-9]*$'
print(re.search(pattern,input_num))