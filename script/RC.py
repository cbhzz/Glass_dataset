import numpy as np

from osgeo import gdal
import os

band_name = ["BSA_VIS", 'WSA_VIS', 'BSA_NIR', 'WSA_NIR',  'BSA_shortwave', 'WSA_shortwave']

path_old = r"E:\Tibet Plateau\dataset3\Glass_Albedo_1km"

path1_new = r"E:\Tibet Plateau\dataset9\Glass_Albedo_1km"


def multiply_raster(input_file, output_file, factor):
    # 打开栅格文件
    raster_ds = gdal.Open(input_file)
    if raster_ds is None:
        print(f"Cannot open raster file: {input_file}")
        return

    # 读取栅格数据为NumPy数组
    band = raster_ds.GetRasterBand(1)
    raster_data = band.ReadAsArray().astype(np.float32)
    # 将每个像素值乘以一个数
    raster_data = raster_data * factor
    print(raster_data.max())
    # 获取栅格文件的地理变换和投影
    geotransform = raster_ds.GetGeoTransform()
    projection = raster_ds.GetProjection()

    # 创建输出栅格文件
    
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)

    # 设置输出栅格的地理变换和投影
    out_ds.SetGeoTransform(geotransform)
    out_ds.SetProjection(projection)

    # 写入修改后的数据
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(raster_data)

    # 关闭数据集
    raster_ds = None
    out_ds = None
    print(f'Modified raster saved as {output_file}')




for year in range(2001,2020):
    for bn in band_name:
        for dir_name in os.listdir(path_old+os.sep+str(year)+os.sep+bn):
            file1 = path_old+os.sep+str(year)+os.sep+bn+os.sep+dir_name
            file2 = path1_new+os.sep+str(year)+os.sep+bn+os.sep+dir_name
            multiply_raster(file1, file2, 0.0001)
