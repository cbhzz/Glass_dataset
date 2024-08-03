import os
from osgeo import gdal

# 文件路径
path = r"E:\Tibet Plateau\dataset\Glass_Albedo_1km"
path1 = r"E:\Tibet Plateau\dataset1\Glass_Albedo_1km"

band_name = ["BSA_VIS", 'WSA_VIS', 'QC_VIS', 'BSA_NIR', 'WSA_NIR', 'QC_NIR', 'BSA_shortwave', 'WSA_shortwave', 'QC_shortwave']

# 创建新文件夹
for year in range(2001, 2020):
    year_path = os.path.join(path1, str(year))
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    for bn in band_name:
        band_path = os.path.join(year_path, bn)
        if not os.path.exists(band_path):
            os.makedirs(band_path)

# 读取和处理文件
for year in range(2008, 2020):
    year_dir = os.path.join(path, str(year))
    if not os.path.exists(year_dir):
        print(f"Year directory does not exist: {year_dir}")
        continue
    for dir_name in os.listdir(year_dir):
        file_path = os.path.join(year_dir, dir_name)
        if not os.path.isfile(file_path):
            print(f"File does not exist: {file_path}")
            continue
        try:
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

                # 修正正的 NS 分辨率
                if geo_transform[5] > 0:
                    geo_transform = geo_transform[:5] + (-abs(geo_transform[5]),)

                # 生成输出文件路径
                out_file = os.path.join(path1, str(year), band_name[i], dir_name.replace('.hdf', '') + '.tif')

                # 创建输出文件
                driver = gdal.GetDriverByName('GTiff')
                out_ds = driver.Create(out_file, band.RasterXSize, band.RasterYSize, 1, gdal.GDT_Float32)
                out_ds.SetGeoTransform(geo_transform)
                out_ds.SetProjection(projection)
                out_ds.GetRasterBand(1).WriteArray(band_array)
                out_ds.FlushCache()
                out_ds = None
                band = None
            image_collections = None
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
