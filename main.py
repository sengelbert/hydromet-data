import json
import click
import requests
import pandas as pd
import matplotlib.pyplot as plt

@click.command()
@click.option('-st', '--station', default='GRARESCO', help='Station', type=str)
@click.option('-sy', '--start_year', default='2010', help='Start Year', type=str)
@click.option('-sm', '--start_month', default='01', help='Start Month', type=str)
@click.option('-sd', '--start_day', default='01', help='Start Day', type=str)
@click.option('-ey', '--end_year', default='2023', help='End Year', type=str)
@click.option('-em', '--end_month', default='05', help='End Month', type=str)
@click.option('-ed', '--end_day', default='05', help='End Day', type=str)
@click.option('-pa', '--parameters', default='FB, AF, IN, IN_NAT, QD', help='Parameters comma separated', type=str)
def process(station, start_year, start_month, start_day, end_year, end_month, end_day, parameters):
    base_url = 'https://www.usbr.gov/gp-bin/arcread.pl?'
    params = ["pa="+p.strip()+"&" for p in parameters.split(',')]
    metric_parameters = ''.join(params)
    url_params = {'st': station, 'by': start_year, 'bm': start_month, 'bd': start_day, 'ey': end_year, 'em': end_month, 'ed': end_day}
    url_suffix = [k+"="+v+"&" for k, v in url_params.items()]
    url_parameters = ''.join(url_suffix) + metric_parameters
    url = base_url + url_parameters + "json=1"

    response = requests.get(url)
    json_data = json.loads(response.text)

    # Put in DF and format, clean, whatever. Yeah this is specific to the station I care about
    df = pd.DataFrame(json_data["SITE"]["DATA"])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['FB'] = df['FB'].astype(float)
    df['AF'] = df['AF'].astype(float)
    df.drop(df[df['FB'] < 8200].index, inplace=True)
    df.drop(df[df['FB'] > 8290].index, inplace=True)
    df['Year'] = df['DATE'].dt.strftime('%Y')
    df['Month'] = df['DATE'].dt.strftime('%m')
    print(df)
    df.info()

    # Troubleshoot data
    # df.to_csv('out/out.csv')

    # Plot Playtime
    # Plot All Dates
    df.plot(x='DATE', y='FB', kind='line')
    plt.show()

    # Pivot to yearly chart
    pv = pd.pivot_table(df, index='Month', columns='Year',
                        values='FB')
    pv.plot()
    plt.show()

if __name__ == '__main__':
    process()
