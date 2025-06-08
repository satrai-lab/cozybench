from eppy import modeleditor
from eppy.modeleditor import IDF

# 设置IDF和IDD文件路径
idf_path = r"C:\Users\XiaoMA\Desktop\DoE buildings\FRA_Paris.Orly.071490_IWEC\RefBldgSecondarySchoolNew2004_v1.4_7.2_1A_USA_FL_MIAMI.idf"
# 读取IDF文件内容
with open(idf_path, 'r') as file:
    idf_content = file.readlines()

# 查找所有的Zone对象
zone_count = 0
zone_names = []
inside_zone_block = False

for line in idf_content:
    line = line.strip()
    if line.lower().startswith("zone,"):
        zone_count += 1
        inside_zone_block = True
    elif inside_zone_block:
        zone_name = line.split(',')[0]  # 提取Zone名称
        zone_names.append(zone_name)
        inside_zone_block = False

# 打印Zone数量
print(f"Number of Zones in the IDF file: {zone_count}")

# 可选：打印每个Zone的名称
for zone_name in zone_names:
    print(f"Zone Name: {zone_name}")