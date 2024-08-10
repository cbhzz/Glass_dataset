import os

from osgeo import gdal, ogr

# 输入矢量文件路径
shp_path = r"E:\Tibet Plateau\GIS\shp\TPBoundary_HF.shp"

# 输入和输出栅格数据路径
path1_new = r"E:\Tibet Plateau\dataset9\Glass_Albedo_1km"

# 波段名称列表
band_name = ["BSA_VIS", 'WSA_VIS',  'BSA_NIR', 'WSA_NIR',
              'BSA_shortwave', 'WSA_shortwave']


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
        nodata_value = -0.9999# 如果没有无效值，使用默认值

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
        dstNodata=nodata_value  # 设置无效值
    )

    # 执行重投影和裁剪
    gdal.Warp(output_file, raster_ds, options=warp_options)

    # 关闭数据集
    raster_ds = None
    vector_ds = None


if __name__ == '__main__':
    target_proj_wkt = get_vector_projection(shp_path)
    if target_proj_wkt is None:
        print("Failed to get projection from vector file.")
    else:
        for bn in band_name:
            for i in range(1, 365, 8):
                d2 = os.path.join(path1_new, bn, f"day_{i}.tif")  # 栅格数据文件路径
                d3 = os.path.join(path1_new, bn, f"day_{i}.tif")  # 重投影并裁剪后的栅格数据文件路径

                # 创建输出目录（如果不存在）
                if not os.path.exists(os.path.dirname(d3)):
                    os.makedirs(os.path.dirname(d3))

                # 重投影和裁剪
                reproject_and_clip_raster(d2, d3, target_proj_wkt, shp_path)
                print(f'Reprojected and clipped raster saved as {d3}')
