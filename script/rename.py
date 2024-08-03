import os
path1 = r"E:\Tibet Plateau\dataset1\Glass_Albedo_1km"
path = r"E:\a"

band_name = ["BSA_VIS", 'WSA_VIS', 'QC_VIS', 'BSA_NIR', 'WSA_NIR', 'QC_NIR', 'BSA_shortwave', 'WSA_shortwave', 'QC_shortwave']
for name in os.listdir(path):
    out_file = (path1 + os.sep + str(name.split('.')[-3][1:5]) + os.sep + band_name[1] + os.sep + name.replace('.hdf','') + '.tif')
    print(out_file)

