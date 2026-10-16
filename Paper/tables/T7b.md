| Variant | Init | Acc. | Mean conf. | ECE raw | ECE after temp. scaling | NLL raw |
|---|---|---|---|---|---|---|
| base (label smoothing 0.1, class weights) | ImageNet | 0.911 | 0.753 | 0.200 ± 0.005 | 0.078 ± 0.020 | 0.497 |
| base (label smoothing 0.1, class weights) | ImageNet → rice | 0.899 | 0.753 | 0.198 ± 0.022 | 0.088 ± 0.009 | 0.518 |
| no label smoothing | ImageNet | 0.928 | 0.978 | 0.063 ± 0.004 | 0.049 ± 0.007 | 0.345 |
| no label smoothing | ImageNet → rice | 0.912 | 0.983 | 0.084 ± 0.014 | 0.048 ± 0.005 | 0.412 |
| no class weights | ImageNet | 0.947 | 0.897 | 0.063 ± 0.012 | 0.032 ± 0.003 | 0.234 |
| no class weights | ImageNet → rice | 0.933 | 0.904 | 0.059 ± 0.013 | 0.036 ± 0.002 | 0.263 |
| neither | ImageNet | 0.944 | 0.980 | 0.053 ± 0.003 | 0.043 ± 0.001 | 0.245 |
| neither | ImageNet → rice | 0.931 | 0.987 | 0.059 ± 0.011 | 0.040 ± 0.008 | 0.297 |
| 80 epochs | ImageNet | 0.936 | 0.758 | 0.234 ± 0.020 | 0.083 ± 0.008 | 0.534 |
| 80 epochs | ImageNet → rice | 0.915 | 0.763 | 0.223 ± 0.005 | 0.090 ± 0.011 | 0.551 |
