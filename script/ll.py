import os
import numpy as np
from osgeo import gdal, ogr

# 输入矢量文件路径
shp_path = r"E:\Tibet Plateau\GIS\shp\TPBoundary_HF.shp"

# 输入和输出栅格数据路径
path = r"E:\Tibet Plateau\dataset2\Glass_Albedo_1km"
path1 = r"E:\Tibet Plateau\dataset3\Glass_Albedo_1km"

# 波段名称列表
band_name = ["BSA_VIS", 'WSA_VIS', 'QC_VIS', 'BSA_NIR', 'WSA_NIR',
             'QC_NIR', 'BSA_shortwave', 'WSA_shortwave', "QC_shortwave"]

band_name1 = ["BSA_VIS", 'WSA_VIS', 'BSA_NIR', 'WSA_NIR', 'BSA_shortwave', 'WSA_shortwave']

path1_new = r"E:\Tibet Plateau\dataset9\Glass_Albedo_1km"


def get_vector_projection(vector_file):
    vector_ds = ogr.Open(vector_file)
    if vector_ds is None:
        print(f"Cannot open vector file: {vector_file}")
        return None
    layer = vector_ds.GetLayer()
    spatial_ref = layer.GetSpatialRef()
    proj_wkt = spatial_ref.ExportToWkt()
    vector_ds = None
    return proj_wkt


def get_nodata_value(raster_file):
    raster_ds = gdal.Open(raster_file)
    if raster_ds is None:
        print(f"Cannot open raster file: {raster_file}")
        return None
    band = raster_ds.GetRasterBand(1)
    nodata_value = band.GetNoDataValue()
    print(nodata_value)
    raster_ds = None
    return nodata_value


def reproject_and_clip_raster(raster_file, output_file, target_proj_wkt, vector_file):
    # 检查栅格文件是否存在
    if not os.path.exists(raster_file):
        print(f"Raster file does not exist: {raster_file}")
        return

    # 打开栅格数据集
    raster_ds = gdal.Open(raster_file)
    if raster_ds is None:
        print(f"Cannot open raster file: {raster_file}")
        return

    # 获取无效值
    nodata_value = get_nodata_value(raster_file)
    if nodata_value is None:
        nodata_value = -0.0001  # 如果没有无效值，使用默认值

    # 打开矢量数据集
    vector_ds = ogr.Open(vector_file)
    if vector_ds is None:
        print(f"Cannot open vector file: {vector_file}")
        return
    layer = vector_ds.GetLayer()
    xmin, xmax, ymin, ymax = layer.GetExtent()

    warp_options = gdal.WarpOptions(
        dstSRS=target_proj_wkt,
        outputBounds=(xmin, ymin, xmax, ymax),
        cutlineDSName=vector_file,
        cropToCutline=True,
        dstNodata=nodata_value
    )

    # 执行重投影和裁剪
    gdal.Warp(output_file, raster_ds, options=warp_options)

    # 关闭数据集
    raster_ds = None
    vector_ds = None


def multiply_raster(input_file, output_file, factor, new_nodata_value):
    # 打开栅格文件
    raster_ds = gdal.Open(input_file)
    if raster_ds is None:
        print(f"Cannot open raster file: {input_file}")
        return

    # 读取栅格数据为NumPy数组
    band = raster_ds.GetRasterBand(1)
    raster_data = band.ReadAsArray().astype(np.float32)

    # 获取当前的 NoData 值
    nodata_value = band.GetNoDataValue()
    if nodata_value is None:
        nodata_value = -1  # 如果没有无效值，使用默认值

    # 将每个像素值乘以一个数
    raster_data = raster_data * factor

    # 将旧的 NoData 值替换为新的 NoData 值
    raster_data[raster_data == nodata_value * factor] = new_nodata_value

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

    # 设置新的 NoData 值
    out_band.SetNoDataValue(new_nodata_value)

    # 关闭数据集
    raster_ds = None
    out_ds = None
    print(f'Modified raster saved as {output_file}')


# 创建文件夹
for year in range(2001, 2020):
    year_path = os.path.join(path1, str(year))
    if not os.path.exists(year_path):
        os.makedirs(year_path)
    for bn in band_name1:
        band_path = os.path.join(year_path, bn)
        if not os.path.exists(band_path):
            os.makedirs(band_path)

for year in range(2002, 2020):
 for bn in band_name1:
   for dir_name in os.listdir(path + os.sep + str(year) + os.sep + bn):
        file1 = path + os.sep + str(year) + os.sep + bn + os.sep + dir_name
        file2 = path1 + os.sep + str(year) + os.sep + bn + os.sep + dir_name
        multiply_raster(file1, file2, 0.0001, -0.0001)

if __name__ == '__main__':
    target_proj_wkt = get_vector_projection(shp_path)
    if target_proj_wkt is None:
        print("Failed to get projection from vector file.")
    else:
        for year in range(2002, 2020):
            for bn in band_name1:
                for i in range(1, 365, 8):
                    d2 = os.path.join(path1, str(year),bn, f"day_{i}.tif")  # 栅格数据文件路径
                    d3 = os.path.join(path1_new, str(year), bn, f"day_{i}.tif")  # 重投影并裁剪后的栅格数据文件路径

                    # 创建输出目录（如果不存在）
                    if not os.path.exists(os.path.dirname(d3)):
                        os.makedirs(os.path.dirname(d3))

                    # 重投影和裁剪
                    reproject_and_clip_raster(d2, d3, target_proj_wkt, shp_path)
                    print(f'Reprojected and clipped raster saved as {d3}')
