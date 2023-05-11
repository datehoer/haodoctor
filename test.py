import re

data = ['\n        ', '病例信息', '\n            ', '疾病描述:', '\n                ', '运动后心脏难受,右冠后降支堵的厉害是不是和这次运动心脏彩超吻合?刘医生给好好看看给个建议(2023-05-11填写)', '\n                ', '运动心脏彩超显示阳性,运动后背后背疼(2023-05-11填写)', '\n                ', '刘能给我办个住院吗?明天一块做手术,今天做这个差点又心梗,→有一年半之前的感觉了(2023-05-11填写)', '\n            ', '身高体重:', '\n                ', '175cm,69kg(2023-05-06测量)', '\n            ', '疾病:', '\n                ', '冠状动脉药物球囊扩张术后3月(2023-05-06填写)', '\n                ', '胸前区扩散疼痛三分钟,左后背疼(2023-05-11填写)', '\n            ', '过敏史:', '\n                ', '无(2023-05-06填写)', '\n            ', '希望获得的帮助:', '\n                ', '接下来您有什么建议', '\n      ']

# 匹配疾病描述
disease_desc = re.search('疾病描述:(.*)身高体重', '\n'.join(data), re.S)
print("疾病描述", disease_desc.group(1).strip())

# 匹配身高体重
height_weight = re.search('身高体重:(.*)疾病', '\n'.join(data), re.S)
print("身高体重", height_weight.group(1).strip())

# 匹配疾病
disease = re.search('疾病:(.*)过敏史', '\n'.join(data), re.S)
print("疾病", disease.group(1).strip())

# 匹配过敏史
allergy = re.search('过敏史:(.*)希望获得的帮助', '\n'.join(data), re.S)
print("过敏史", allergy.group(1).strip())

# 匹配希望获得的帮助
help_needed = re.search('希望获得的帮助:(.*)', '\n'.join(data), re.S)
print("希望获得的帮助", help_needed.group(1).strip())
