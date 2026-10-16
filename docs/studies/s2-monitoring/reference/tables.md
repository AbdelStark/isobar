# S2 monitoring sensitivity: generated tables

Generated from the adjacent JSON reports by `scripts/sensitivity_study.py`.
Post-run truth from synthetic fixtures; no policy ranking or empirical claim.

Cells show mean [95% normal-approximation Monte Carlo interval]; n=valid runs
or pairs. Differences are reciprocal minus unrestricted. Undefined denominators
stay undefined. Intervals condition on each model configuration, exclude structural
uncertainty and can have poor coverage at 20 seeds. All terminal runs are retained.
Ratios are averaged over runs, not pooled; privacy is exposure per audit record.

## Sensitivity across conditions

Each column is a separate paired policy contrast; these conditions are not pooled.

| Metric | f01-r00 | f01-r30 | f10-r00 | f10-r30 |
|---|---:|---:|---:|---:|
| `appeal_resolution_fraction` | undefined; n=0 | undefined; n=0 | undefined; n=0 | undefined; n=0 |
| `appeal_success_fraction` | undefined; n=0 | undefined; n=0 | undefined; n=0 | undefined; n=0 |
| `auditability_fraction` | undefined; n=0 | undefined; n=0 | undefined; n=0 | undefined; n=0 |
| `authority_concentration` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `breaches` | 3.95 [3.13969, 4.76031]; n=20 | 8.4 [6.78249, 10.0175]; n=20 | 3.35 [2.77636, 3.92364]; n=20 | 7.15 [5.61014, 8.68986]; n=20 |
| `control_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `cooperation_fraction` | undefined; n=0 | undefined; n=0 | undefined; n=0 | undefined; n=0 |
| `denial_fraction` | -0.0358073 [-0.053709, -0.0179056]; n=20 | 0.0235842 [0.00583747, 0.0413309]; n=20 | -0.0308342 [-0.046747, -0.0149214]; n=20 | 0.0119384 [-0.00409969, 0.0279764]; n=20 |
| `misuse_incidents` | -0.05 [-0.148, 0.048]; n=20 | -0.05 [-0.148, 0.048]; n=20 | -0.05 [-0.148, 0.048]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `power_concentration` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | undefined; n=0 | undefined; n=0 | undefined; n=0 |
| `readiness_gap` | -1.73619 [-1.85265, -1.61972]; n=20 | -1.39098 [-1.55626, -1.22571]; n=20 | -1.74109 [-1.86326, -1.61892]; n=20 | -1.54464 [-1.70652, -1.38276]; n=20 |
| `service_total` | 10.3125 [5.15681, 15.4682]; n=20 | -6.79225 [-11.9033, -1.68119]; n=20 | 8.88025 [4.29737, 13.4631]; n=20 | -3.43825 [-8.05721, 1.18071]; n=20 |

## f01-r00

[Saved comparison](f01-r00.json): false-positive rate 0.01, shared-root failure 0.0; horizon 24.

- unrestricted: 20 completed, 0 terminal; [seed-0 replay bundle](f01-r00-unrestricted-seed0.json).
- reciprocal: 20 completed, 0 terminal; [seed-0 replay bundle](f01-r00-reciprocal-seed0.json).

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `appeal_resolution_fraction` | undefined; n=0 | 1 [1, 1]; n=18 | undefined; n=0 |
| `appeal_success_fraction` | undefined; n=0 | 0.0819685 [0.0202277, 0.143709]; n=18 | undefined; n=0 |
| `auditability_fraction` | undefined; n=0 | 1 [1, 1]; n=18 | undefined; n=0 |
| `authority_concentration` | 0.5 [0.5, 0.5]; n=20 | 0.5 [0.5, 0.5]; n=20 | 0 [0, 0]; n=20 |
| `breaches` | 0 [0, 0]; n=20 | 3.95 [3.13969, 4.76031]; n=20 | 3.95 [3.13969, 4.76031]; n=20 |
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `cooperation_fraction` | undefined; n=0 | 0.890278 [0.867769, 0.912787]; n=20 | undefined; n=0 |
| `denial_fraction` | 0.326771 [0.314991, 0.338551]; n=20 | 0.290964 [0.272041, 0.309886]; n=20 | -0.0358073 [-0.053709, -0.0179056]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `power_concentration` | 0.504132 [0.504132, 0.504132]; n=20 | 0.504132 [0.504132, 0.504132]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `readiness_gap` | 2.4313 [2.37613, 2.48648]; n=20 | 0.695115 [0.58732, 0.802911]; n=20 | -1.73619 [-1.85265, -1.61972]; n=20 |
| `service_total` | 193.89 [190.497, 197.283]; n=20 | 204.203 [198.753, 209.652]; n=20 | 10.3125 [5.15681, 15.4682]; n=20 |

### Aurora (aurora)

Synthetic population weight: 1.0.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.25 [0.25, 0.25]; n=20 | 0.298698 [0.277489, 0.319907]; n=20 | 0.0486979 [0.0274891, 0.0699067]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 108 [108, 108]; n=20 | 100.987 [97.9334, 104.042]; n=20 | -7.0125 [-10.0666, -3.95843]; n=20 |
| `service_per_population` | 108 [108, 108]; n=20 | 100.987 [97.9334, 104.042]; n=20 | -7.0125 [-10.0666, -3.95843]; n=20 |

### Boreal (boreal)

Synthetic population weight: 1.2.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.403542 [0.379982, 0.427101]; n=20 | 0.283229 [0.260913, 0.305545]; n=20 | -0.120313 [-0.143217, -0.0974084]; n=20 |
| `misuse_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 85.89 [82.4974, 89.2826]; n=20 | 103.215 [100.001, 106.429]; n=20 | 17.325 [14.0268, 20.6232]; n=20 |
| `service_per_population` | 71.575 [68.7478, 74.4022]; n=20 | 86.0125 [83.3346, 88.6904]; n=20 | 14.4375 [11.689, 17.186]; n=20 |

## f01-r30

[Saved comparison](f01-r30.json): false-positive rate 0.01, shared-root failure 0.3; horizon 24.

- unrestricted: 20 completed, 0 terminal; [seed-0 replay bundle](f01-r30-unrestricted-seed0.json).
- reciprocal: 20 completed, 0 terminal; [seed-0 replay bundle](f01-r30-reciprocal-seed0.json).

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `appeal_resolution_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `appeal_success_fraction` | undefined; n=0 | 0.0543056 [0.0116028, 0.0970083]; n=20 | undefined; n=0 |
| `auditability_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `authority_concentration` | 0.5 [0.5, 0.5]; n=20 | 0.5 [0.5, 0.5]; n=20 | 0 [0, 0]; n=20 |
| `breaches` | 0 [0, 0]; n=20 | 8.4 [6.78249, 10.0175]; n=20 | 8.4 [6.78249, 10.0175]; n=20 |
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `cooperation_fraction` | undefined; n=0 | 0.766667 [0.721736, 0.811597]; n=20 | undefined; n=0 |
| `denial_fraction` | 0.326771 [0.314991, 0.338551]; n=20 | 0.350355 [0.328188, 0.372522]; n=20 | 0.0235842 [0.00583747, 0.0413309]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `power_concentration` | 0.504132 [0.504132, 0.504132]; n=20 | 0.504132 [0.504132, 0.504132]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `readiness_gap` | 2.4313 [2.37613, 2.48648]; n=20 | 1.04032 [0.868079, 1.21256]; n=20 | -1.39098 [-1.55626, -1.22571]; n=20 |
| `service_total` | 193.89 [190.497, 197.283]; n=20 | 187.098 [180.714, 193.482]; n=20 | -6.79225 [-11.9033, -1.68119]; n=20 |

### Aurora (aurora)

Synthetic population weight: 1.0.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.25 [0.25, 0.25]; n=20 | 0.361684 [0.334636, 0.388732]; n=20 | 0.111684 [0.0846362, 0.138732]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 108 [108, 108]; n=20 | 91.9175 [88.0226, 95.8124]; n=20 | -16.0825 [-19.9774, -12.1876]; n=20 |
| `service_per_population` | 108 [108, 108]; n=20 | 91.9175 [88.0226, 95.8124]; n=20 | -16.0825 [-19.9774, -12.1876]; n=20 |

### Boreal (boreal)

Synthetic population weight: 1.2.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.403542 [0.379982, 0.427101]; n=20 | 0.339026 [0.314196, 0.363856]; n=20 | -0.0645156 [-0.0823807, -0.0466505]; n=20 |
| `misuse_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 85.89 [82.4974, 89.2826]; n=20 | 95.1803 [91.6048, 98.7557]; n=20 | 9.29025 [6.71768, 11.8628]; n=20 |
| `service_per_population` | 71.575 [68.7478, 74.4022]; n=20 | 79.3169 [76.3373, 82.2964]; n=20 | 7.74188 [5.59806, 9.88569]; n=20 |

## f10-r00

[Saved comparison](f10-r00.json): false-positive rate 0.1, shared-root failure 0.0; horizon 24.

- unrestricted: 20 completed, 0 terminal; [seed-0 replay bundle](f10-r00-unrestricted-seed0.json).
- reciprocal: 20 completed, 0 terminal; [seed-0 replay bundle](f10-r00-reciprocal-seed0.json).

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `appeal_resolution_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `appeal_success_fraction` | undefined; n=0 | 0.537877 [0.435086, 0.640668]; n=20 | undefined; n=0 |
| `auditability_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `authority_concentration` | 0.5 [0.5, 0.5]; n=20 | 0.5 [0.5, 0.5]; n=20 | 0 [0, 0]; n=20 |
| `breaches` | 0 [0, 0]; n=20 | 3.35 [2.77636, 3.92364]; n=20 | 3.35 [2.77636, 3.92364]; n=20 |
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `cooperation_fraction` | undefined; n=0 | 0.906944 [0.89101, 0.922879]; n=20 | undefined; n=0 |
| `denial_fraction` | 0.326771 [0.314991, 0.338551]; n=20 | 0.295937 [0.283288, 0.308585]; n=20 | -0.0308342 [-0.046747, -0.0149214]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `power_concentration` | 0.504132 [0.504132, 0.504132]; n=20 | 0.504132 [0.504132, 0.504132]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `readiness_gap` | 2.4313 [2.37613, 2.48648]; n=20 | 0.690211 [0.603056, 0.777366]; n=20 | -1.74109 [-1.86326, -1.61892]; n=20 |
| `service_total` | 193.89 [190.497, 197.283]; n=20 | 202.77 [199.127, 206.413]; n=20 | 8.88025 [4.29737, 13.4631]; n=20 |

### Aurora (aurora)

Synthetic population weight: 1.0.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.25 [0.25, 0.25]; n=20 | 0.298186 [0.285025, 0.311347]; n=20 | 0.0481858 [0.0350245, 0.061347]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 108 [108, 108]; n=20 | 101.061 [99.166, 102.956]; n=20 | -6.93875 [-8.83397, -5.04353]; n=20 |
| `service_per_population` | 108 [108, 108]; n=20 | 101.061 [99.166, 102.956]; n=20 | -6.93875 [-8.83397, -5.04353]; n=20 |

### Boreal (boreal)

Synthetic population weight: 1.2.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.403542 [0.379982, 0.427101]; n=20 | 0.293687 [0.273134, 0.314241]; n=20 | -0.109854 [-0.133706, -0.0860023]; n=20 |
| `misuse_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 85.89 [82.4974, 89.2826]; n=20 | 101.709 [98.7493, 104.669]; n=20 | 15.819 [12.3843, 19.2537]; n=20 |
| `service_per_population` | 71.575 [68.7478, 74.4022]; n=20 | 84.7575 [82.2911, 87.2239]; n=20 | 13.1825 [10.3203, 16.0447]; n=20 |

## f10-r30

[Saved comparison](f10-r30.json): false-positive rate 0.1, shared-root failure 0.3; horizon 24.

- unrestricted: 20 completed, 0 terminal; [seed-0 replay bundle](f10-r30-unrestricted-seed0.json).
- reciprocal: 20 completed, 0 terminal; [seed-0 replay bundle](f10-r30-reciprocal-seed0.json).

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `appeal_resolution_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `appeal_success_fraction` | undefined; n=0 | 0.297228 [0.200443, 0.394012]; n=20 | undefined; n=0 |
| `auditability_fraction` | undefined; n=0 | 1 [1, 1]; n=20 | undefined; n=0 |
| `authority_concentration` | 0.5 [0.5, 0.5]; n=20 | 0.5 [0.5, 0.5]; n=20 | 0 [0, 0]; n=20 |
| `breaches` | 0 [0, 0]; n=20 | 7.15 [5.61014, 8.68986]; n=20 | 7.15 [5.61014, 8.68986]; n=20 |
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `cooperation_fraction` | undefined; n=0 | 0.801389 [0.758615, 0.844163]; n=20 | undefined; n=0 |
| `denial_fraction` | 0.326771 [0.314991, 0.338551]; n=20 | 0.338709 [0.320601, 0.356818]; n=20 | 0.0119384 [-0.00409969, 0.0279764]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `power_concentration` | 0.504132 [0.504132, 0.504132]; n=20 | 0.504132 [0.504132, 0.504132]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `readiness_gap` | 2.4313 [2.37613, 2.48648]; n=20 | 0.886663 [0.7446, 1.02873]; n=20 | -1.54464 [-1.70652, -1.38276]; n=20 |
| `service_total` | 193.89 [190.497, 197.283]; n=20 | 190.452 [185.236, 195.667]; n=20 | -3.43825 [-8.05721, 1.18071]; n=20 |

### Aurora (aurora)

Synthetic population weight: 1.0.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.25 [0.25, 0.25]; n=20 | 0.334991 [0.313048, 0.356935]; n=20 | 0.0849913 [0.0630476, 0.106935]; n=20 |
| `misuse_incidents` | 0.05 [-0.048, 0.148]; n=20 | 0 [0, 0]; n=20 | -0.05 [-0.148, 0.048]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 108 [108, 108]; n=20 | 95.7612 [92.6014, 98.9211]; n=20 | -12.2388 [-15.3986, -9.07885]; n=20 |
| `service_per_population` | 108 [108, 108]; n=20 | 95.7612 [92.6014, 98.9211]; n=20 | -12.2388 [-15.3986, -9.07885]; n=20 |

### Boreal (boreal)

Synthetic population weight: 1.2.

| Metric | Unrestricted | Reciprocal | Paired difference |
|---|---:|---:|---:|
| `control_incidents` | 0.1 [-0.0348965, 0.234896]; n=20 | 0.1 [-0.0348965, 0.234896]; n=20 | 0 [0, 0]; n=20 |
| `denial_fraction` | 0.403542 [0.379982, 0.427101]; n=20 | 0.342427 [0.319223, 0.365631]; n=20 | -0.0611146 [-0.0784029, -0.0438262]; n=20 |
| `misuse_incidents` | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 | 0 [0, 0]; n=20 |
| `privacy_fraction` | undefined; n=0 | 0.1 [0.1, 0.1]; n=20 | undefined; n=0 |
| `service` | 85.89 [82.4974, 89.2826]; n=20 | 94.6905 [91.3492, 98.0318]; n=20 | 8.8005 [6.31098, 11.29]; n=20 |
| `service_per_population` | 71.575 [68.7478, 74.4022]; n=20 | 78.9088 [76.1243, 81.6932]; n=20 | 7.33375 [5.25915, 9.40835]; n=20 |
