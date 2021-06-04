import argparse
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.options.plotting.backend = "plotly"

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", default='data', help='path to VACC queue data folder.')
args = parser.parse_args()

now = datetime.now()
current_time = now.strftime("%A, %B %d, %Y %I:%M:%S")
timestamp = datetime.timestamp(now)

cluster_settings = {
    'bluemoon': {
        'name': 'bluemoon',
        'partitions': ['ib', 'short', 'bigmemwk', 'bigmem', 'bluemoon', 'bluemoon*', 'week'],
    },
    'deepgreen': {
        'name': 'deepgreen',
        'partitions': ['dggpu', 'dggpu*', 'dg-jup'],
    },
    'blackdiamond': {
        'name': 'bluemoon',
        'partitions': ['bdgpu'],
    }
}

def get_total_resources(cluster='bluemoon'):
    c = cluster_settings[cluster]

    df = pd.read_csv(f"{args.database}/{c['name']}.assets.txt", delim_whitespace=True).drop_duplicates(subset='NODELIST')
    df = df[df['PARTITION'].isin(cluster_settings[cluster]['partitions'])]
    df['GPU'] = df['GRES'].str.extract(r'gpu:(\d+)').fillna(0).astype(int)
    ret = {
        'cpu': df['CPUS'].sum(),
        'gpu' : df['GPU'].sum(),
        'mem': df['MEMORY'].sum() / 1024.,
    }
    return ret

for key, value in cluster_settings.items():
    value.update(get_total_resources(cluster=key))

def get_resources_amount(cluster='bluemoon', status='running'):
    c = cluster_settings[cluster]

    df = pd.read_csv(f"{args.database}/{c['name']}.queue.txt", delim_whitespace=True)
    df = df[df['PARTITION'].isin(c['partitions'])]
    df['MEM_G'] = df['TRES_ALLOC'].str.extract(r'mem=(\d+)G').fillna(0).astype(float)
    df['MEM_M'] = df['TRES_ALLOC'].str.extract(r'mem=(\d+)M').fillna(0).astype(float)
    df['MEM'] = df['MEM_G'] + df['MEM_M']/1024.
    df['GPU'] = df['TRES_ALLOC'].str.extract(r'gres/gpu=(\d+)').fillna(0).astype(float)
    df['CPU'] = df['TRES_ALLOC'].str.extract(r'cpu=(\d+)').fillna(0).astype(float)

    if status=='running':
        df_status = df[df['EXEC_HOST'].notna()]
    else:
        df_status = df[df['EXEC_HOST'].isna()]

    # if cluster=='deepgreen' and status=='running':
    #     print(c['partitions'])
    #     print(df_status)

    cpu = df_status['CPU'].sum()
    gpu = df_status['GPU'].sum()
    mem = df_status['MEM'].sum()
    print(f"{cluster}/{status}:  cpu: {cpu}/{c['cpu']}, gpu: {gpu}/{c['gpu']}, mem: {mem}/{c['mem']}")
    ret = {
        f'{status}_CPU': cpu,
        f'{status}_CPU_percentage': cpu / c['cpu'],
        f'{status}_GPU': gpu,
        f'{status}_GPU_percentage': 0 if c['gpu']==0 else gpu / c['gpu'],
        f'{status}_MEM': mem,
        f'{status}_MEM_percentage': mem/c['mem'],
    }
    return ret

for key, value in cluster_settings.items():
    value.update(get_resources_amount(cluster=key, status='waiting'))
    value.update(get_resources_amount(cluster=key, status='running'))

print(cluster_settings)

fig = make_subplots(rows=1, cols=3, subplot_titles=list(cluster_settings.keys()))

resource_cols = ['CPU', 'GPU', 'MEM'][::-1]
for i, (key,value) in enumerate(cluster_settings.items()):
    fig.add_trace(
        go.Bar(
            name='Busy',
            legendgroup = 'Busy',
            y = resource_cols,
            x = [value[f'running_{_c}_percentage'] for _c in resource_cols],
            orientation='h',
            marker=dict(
                color='#f23c06',
                # line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            ),
            showlegend=i==0,
        ),
        row=1, col=i+1,
    )
    fig.add_trace(
        go.Bar(
            name='Idle',
            legendgroup='Idle',
            y = resource_cols,
            x = [1-value[f'running_{_c}_percentage'] for _c in resource_cols],
            orientation='h',
            marker=dict(
                color='#cccccc',
                # line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            ),
            showlegend=i==0,
        ),
        row=1, col=i+1,
    )
    fig.add_trace(
        go.Bar(
            name='Queue',
            legendgroup='Queue',
            y = resource_cols,
            x = [value[f'waiting_{_c}_percentage'] for _c in resource_cols],
            orientation='h',
            marker=dict(
                color='#fef764',
                # line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
            ),
            showlegend=i==0,
        ),
        row=1, col=i+1,
    )

fig.update_xaxes(
    title_text='Percentage of total resources',
    tickformat= ',.0%',
    range=[0,3],
)
fig.update_layout(
    barmode='stack',
    # showlegend=False,
    font_size=16,
    title=f"Current Resource Usage / Queue (Generated at {current_time})",
)

fig.write_html("public_html/queue.plots.html", default_height=300)
