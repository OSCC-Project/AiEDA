raw =     {
        "skew_bound": "0.08",
        "max_buf_tran": "1.0",
        "max_sink_tran": "1.0",
        "max_cap": "0.15",
        "max_fanout": "32",
        "min_length": "50",
        "max_length": "300",
        "scale_size": 50,
        "cluster_size": 32,
        "shift_level": 1,
        "latency_opt_level": 1,
        "global_latency_opt_ratio": "0.5",
        "local_latency_opt_ratio": "0.9",
    }
data = dict()
for k,v in raw.items():
    data[k] = {"description": "[CTS] ", "default": v}
print(data)

