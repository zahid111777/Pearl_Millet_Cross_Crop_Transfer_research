| Comparison | Data | Δ macro-F1 (fold mean) | d_z | 95 % t-CI (folds) | Folds won | Pooled Δ [bootstrap 95 % CI] | Holm p (bootstrap) | Δ bal. acc. | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| ConvNeXt-Tiny: random→rice vs ImageNet | 10 % | -0.160 | -2.02 | [-0.259, -0.062] | 0/5 | -0.164 [-0.208, -0.117] | 0.002 | -0.146 | supported (ConvNeXt ricescratch < ConvNeXt imagenet) |
| ConvNeXt-Tiny: random→rice vs ImageNet | 25 % | -0.149 | -1.61 | [-0.264, -0.034] | 0/5 | -0.138 [-0.185, -0.096] | 0.002 | -0.144 | supported (ConvNeXt ricescratch < ConvNeXt imagenet) |
| ConvNeXt-Tiny: random→rice vs ImageNet | 50 % | -0.126 | -1.58 | [-0.225, -0.027] | 0/5 | -0.126 [-0.169, -0.085] | 0.002 | -0.126 | supported (ConvNeXt ricescratch < ConvNeXt imagenet) |
| ConvNeXt-Tiny: random→rice vs ImageNet | 100 % | -0.054 | -0.69 | [-0.151, +0.043] | 1/5 | -0.048 [-0.088, -0.009] | 0.015 | -0.028 | supported (ConvNeXt ricescratch < ConvNeXt imagenet) |
| ConvNeXt-Tiny: ImageNet→rice vs random→rice | 10 % | +0.168 | +2.17 | [+0.072, +0.265] | 5/5 | +0.179 [+0.128, +0.227] | 0.002 | +0.163 | supported (ConvNeXt rice > ConvNeXt ricescratch) |
| ConvNeXt-Tiny: ImageNet→rice vs random→rice | 25 % | +0.139 | +1.45 | [+0.020, +0.257] | 5/5 | +0.116 [+0.072, +0.163] | 0.002 | +0.113 | supported (ConvNeXt rice > ConvNeXt ricescratch) |
| ConvNeXt-Tiny: ImageNet→rice vs random→rice | 50 % | +0.116 | +1.47 | [+0.018, +0.214] | 5/5 | +0.103 [+0.045, +0.162] | 0.002 | +0.098 | supported (ConvNeXt rice > ConvNeXt ricescratch) |
| ConvNeXt-Tiny: ImageNet→rice vs random→rice | 100 % | +0.061 | +0.87 | [-0.026, +0.147] | 5/5 | +0.053 [+0.021, +0.086] | 0.002 | +0.033 | supported (ConvNeXt rice > ConvNeXt ricescratch) |
| ViT-B/16: random→rice vs ImageNet | 10 % | -0.085 | -1.09 | [-0.182, +0.011] | 1/5 | -0.090 [-0.126, -0.055] | 0.002 | -0.056 | supported (ViT ricescratch < ViT imagenet) |
| ViT-B/16: random→rice vs ImageNet | 25 % | -0.066 | -1.08 | [-0.142, +0.010] | 0/5 | -0.099 [-0.139, -0.058] | 0.002 | -0.043 | supported (ViT ricescratch < ViT imagenet) |
| ViT-B/16: random→rice vs ImageNet | 50 % | -0.068 | -0.98 | [-0.155, +0.018] | 0/5 | -0.063 [-0.100, -0.029] | 0.002 | -0.053 | supported (ViT ricescratch < ViT imagenet) |
| ViT-B/16: random→rice vs ImageNet | 100 % | -0.077 | -1.44 | [-0.144, -0.011] | 0/5 | -0.056 [-0.086, -0.029] | 0.002 | -0.055 | supported (ViT ricescratch < ViT imagenet) |
| ViT-B/16: ImageNet→rice vs random→rice | 10 % | +0.062 | +1.20 | [-0.002, +0.126] | 5/5 | +0.057 [+0.027, +0.087] | 0.002 | +0.037 | supported (ViT rice > ViT ricescratch) |
| ViT-B/16: ImageNet→rice vs random→rice | 25 % | +0.044 | +0.46 | [-0.075, +0.164] | 4/5 | +0.070 [+0.028, +0.109] | 0.010 | +0.006 | supported (ViT rice > ViT ricescratch) |
| ViT-B/16: ImageNet→rice vs random→rice | 50 % | +0.037 | +0.36 | [-0.091, +0.165] | 2/5 | +0.019 [-0.020, +0.058] | 0.351 | +0.006 | inconclusive |
| ViT-B/16: ImageNet→rice vs random→rice | 100 % | +0.062 | +1.19 | [-0.003, +0.126] | 5/5 | +0.037 [+0.007, +0.069] | 0.028 | +0.040 | supported (ViT rice > ViT ricescratch) |
