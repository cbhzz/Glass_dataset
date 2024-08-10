import requests
import os

base_url = "http://www.glass.umd.edu/Albedo/MODIS/1km/"

years = list(range(2019, 2020))

print(years)
i_values = [101,102, 233,234,"57".zfill(3),148,149,58]
output_folder = r"E:\Tibet Plateau\dataset\Glass_Albedo_1km"

for year in years:
    dirname = output_folder + os.sep + str(year)
    if str(year) not in os.listdir(output_folder):
        os.mkdir(dirname)

    for day in range(1, 362, 8):
        urls = []
        day_str = str(day).zfill(3)
        folder = f"{year}/{str(day).zfill(3)}"
        print(folder)

        for i in i_values:
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h23v05.2020{i}.hdf")
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h24v05.2020{i}.hdf")
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h25v05.2020{i}.hdf")
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h25v06.2020{i}.hdf")
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h26v05.2020{i}.hdf")
         urls.append(f"{base_url}{folder}/GLASS02A06.V40.A{year}{day_str}.h26v06.2020{i}.hdf")
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                filename = url.split("/")[-1].replace('.'+url.split('/')[-1].split('.')[-2], '')
                filepath = output_folder + os.sep + str(year) + os.sep + filename
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded{filename}")
            else:
                None
