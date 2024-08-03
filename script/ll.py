import os
from osgeo import gdal

# 文件路径
path1 = r"E:\a"
output_path = r"E:\Tibet Plateau\dataset1\Glass_Albedo_1km"
band_names = ["BSA_VIS", 'WSA_VIS', 'QC_VIS', 'BSA_NIR', 'WSA_NIR', 'QC_NIR', 'BSA_shortwave', 'WSA_shortwave', 'QC_shortwave']

# 读取和处理文件
for file in os.listdir(path1):
    file_path = os.path.join(path1, file)
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        continue

    image_collections = gdal.Open(file_path)
    if image_collections is None:
        print(f"Unable to open file: {file_path}")
        continue

    image_list = image_collections.GetSubDatasets()
    for i in range(9):
        band = gdal.Open(image_list[i][0])
        if band is None:
            print(f"Unable to open subdataset: {image_list[i][0]}")
            continue

        band_array = band.ReadAsArray()
        # 检查并修正地理参考信息
        geo_transform = band.GetGeoTransform()
        projection = band.GetProjection()
        if geo_transform is None or projection is None:
            print(f"Missing georeference information in subdataset: {image_list[i][0]}")
            continue

        # 修正NS分辨率
        if geo_transform[5] > 0:
            geo_transform = geo_transform[:5] + (-abs(geo_transform[5]),)

        # 生成输出文件路径
        output_file = os.path.join(output_path, file.split('.')[-3][1:5],band_names[i],file.replace('.hdf', '') + '.tif')

        # 创建输出文件
        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(output_file, band.RasterXSize, band.RasterYSize, 1, gdal.GDT_Float32)
        if out_ds is None:
            print(f"Failed to create output file: {output_file}")
            continue

        out_ds.SetGeoTransform(geo_transform)
        out_ds.SetProjection(projection)
        out_ds.GetRasterBand(1).WriteArray(band_array)
        out_ds.FlushCache()
        out_ds = None
        band = None

    image_collections = None
