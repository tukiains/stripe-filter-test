import os.path
import requests
from cloudnetpy.categorize import generate_categorize
from cloudnetpy.plotting import generate_figure

test_cases = {
    'munich': ('2021-05-16', '2021-05-05', '2021-05-08'),
    'hyytiala': ('2021-05-09', '2021-05-10'),
    'palaiseau': ('2021-03-05', ),
    'granada': ('2021-05-11', '2021-05-07'),
    'norunda': ('2021-03-05', ),
    'bucharest': ('2021-03-05', )
}


def _download(site: str, date: str, product: str = None) -> str:
    payload = {'site': site, 'date': date}
    if product is not None:
        payload['product'] = product
        url = 'https://cloudnet.fmi.fi/api/files'
    else:
        url = 'https://cloudnet.fmi.fi/api/model-files'
    metadata = requests.get(url, payload).json()
    if not metadata:
        raise RuntimeError
    metadata = metadata[0]
    filename = metadata['filename']
    if not os.path.isfile(filename):
        print(f"downloading {filename} ...")
        res = requests.get(metadata['downloadUrl'])
        with open(filename, 'wb') as f:
            f.write(res.content)
    return filename


def main():
    for site, dates in test_cases.items():
        input_files = {}
        for date in dates:
            input_files['model'] = _download(site, date)
            for file_type in ('radar', 'lidar'):
                input_files[file_type] = _download(site, date, file_type)
            try:
                input_files['mwr'] = _download(site, date, 'mwr')
            except RuntimeError:
                input_files['mwr'] = _download(site, date, 'radar')

            generate_categorize(input_files, 'categorize.nc')
            generate_figure('categorize.nc',
                            ['ldr', 'Z', 'v', 'v_sigma'],
                            show=False,
                            image_name=f'images/{date}_{site}_filtered')


if __name__ == "__main__":
    main()
