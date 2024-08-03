from osgeo import gdal
import os
from collections import defaultdict


# 定义影像镶嵌函数
def mosaic_images(input_files, output_file):
    # 检查所有输入文件是否存在
    for file in input_files:
        if not os.path.exists(file):
            print(f"Input file does not exist: {file}")
            return

    # 创建VRT虚拟影像
    vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest')
    vrt = gdal.BuildVRT('/vsimem/temp.vrt', input_files, options=vrt_options)

    # 将VRT文件转换为目标格式
    gdal.Translate(output_file, vrt)
    vrt = None


# 定义输入和输出路径
path = r"E:\Tibet Plateau\dataset1\Glass_Albedo_1km"
path_new = r"E:\Tibet Plateau\dataset2\Glass_Albedo_1km"
band_name = ["BSA_VIS", 'WSA_VIS', 'QC_VIS', 'BSA_NIR', 'WSA_NIR',
             'QC_NIR', 'BSA_shortwave', 'WSA_shortwave', 'QC_shortwave']

# 遍历每个波段
for year in range(2001, 2020):
    for bn in band_name:
        path1 = os.path.join(path, str(year), bn)
        dir_list = os.listdir(path1)

        # 按前缀分组影像文件
        grouped_files = defaultdict(list)
        for filename in dir_list:
            prefix = filename.rsplit('.', 2)[0]  # 获取前缀，例如GLASS02A06.V40.A2004001
            grouped_files[prefix].append(filename)

        k = 1
        for prefix, files in grouped_files.items():
            # 每次处理6个影像
            for i in range(0, len(files), 6):
                if i + 6 <= len(files):
                    input_files = [os.path.join(path1, files[j]) for j in range(i, i + 6)]
                else:
                    input_files = [os.path.join(path1, files[j]) for j in range(i, len(files))]

                # 检查输入文件是否存在
                input_files_exist = all(os.path.exists(f) for f in input_files)
                if not input_files_exist:
                    print(f"One or more input files do not exist for day_{k}: {input_files}")
                    continue

                # 定义输出路径
                output_file = os.path.join(path_new, str(year), bn, f"day_{k}.tif")
                k += 8

                # 创建输出目录（如果不存在）
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                # 执行影像镶嵌
                mosaic_images(input_files, output_file)
                print(f'Mosaic image saved as {output_file}')
