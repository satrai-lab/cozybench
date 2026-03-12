# Co-zyBench

Co-zyBench is a benchmark for evaluating thermal comfort control strategies with an EnergyPlus-based co-simulation loop.

The repository entry point for the full benchmark is `main.py`. The core runtime path uses:

- `main.py`
- `occupants.py`
- `comfort_collector.py`
- `strategies.py`
- `sim_ep.py`
- `result_collector.py`

## Requirements

### Operating system

- Windows

### External tool

- `EnergyPlus 22.2.0`

The code uses EnergyPlus IDF models together with the EnergyPlus Python API helper.

### Python

- Python 3.10 or 3.11

### Python packages

Install the Python packages imported by the runtime call graph:

- `colorama`
- `tqdm`
- `eppy`
- `pandas`
- `numpy`
- `pytz`
- `scikit-learn`
- `energyplus_api_helpers`

Example setup:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install colorama tqdm eppy pandas numpy pytz scikit-learn energyplus_api_helpers
```

## Configure EnergyPlus paths

Before the first run, update these paths to match your local EnergyPlus 22.2.0 installation:

- `main.py`: `idd_file`
- `sim_ep.py`: `CoSimulation.ep_path`

`functional_test.py` also accepts these paths as command line arguments:

- `--energyplus-dir`
- `--idd-file`

Example installation path:

```text
C:\EnergyPlusV22-2-0
```

Example IDD path:

```text
C:\EnergyPlusV22-2-0\Energy+.idd
```

## Quick functional test

Run the short functional test first:

```powershell
python functional_test.py
```

This test runs a real EnergyPlus simulation on the small office model with:

- `models/office/CZ4/in.idf`
- `models/office/trajectories`
- `models/office/occ_config.txt`
- city `paris`
- aggregation strategy `majority`
- HVAC controller `fixed_rule`
- a one-day temporary `RunPeriod`

The script creates a temporary model copy in `.functional_test_runtime/functional_test.idf`, runs EnergyPlus, and writes a result file under `results/`.

Optional arguments:

```powershell
python functional_test.py --city paris --start-date 2010-01-01 --days 1
```

Supported `--start-date` months are `1`, `2`, `6`, `7`, `8`, and `12`, because the control loop in `sim_ep.py` is exercised in those months.

Expected output:

- `results/result_<timestamp>/result-functional_test_majority_fixed_rule_1.txt`

## Full benchmark configuration

The full benchmark is configured directly in `main.py`.

Main configuration fields:

- `path_ep_model`
- `path_trajectories`
- `path_profile`
- `hvac_controller`
- `algorithms`
- `cities`

In the committed default setup:

- `path_ep_model = models/synthetic_large/10floors_V2.idf`
- `path_trajectories = models/synthetic_large/trajectories`
- `path_profile = 1200`
- `hvac_controller = ["preference_estimation"]`
- `algorithms = ["majority", "fair", "drift"]`
- `cities = ["paris"]`

`path_profile` can be either:

- a path to an occupant profile file
- an integer occupant count for synthetic occupant generation

## Input files used by the default benchmark run

| Path | Purpose |
| --- | --- |
| `models/synthetic_large/10floors_V2.idf` | building model |
| `models/synthetic_large/trajectories/1.txt` | occupant location trace |
| `models/weathers/paris.epw` | weather file |
| `models/weathers/paris.ddy` | design day file |
| `models/carbon_intensity/FR_2023_hourly.csv` | carbon intensity data |
| `knn/ashrae_comfort_data.csv` | thermal comfort dataset |

## Run the full benchmark

After installing the Python packages and setting the EnergyPlus paths:

```powershell
python main.py
```

The committed default benchmark run uses:

- `models/synthetic_large/10floors_V2.idf`
- `models/synthetic_large/trajectories`
- `1200` synthetic occupants
- city `paris`
- algorithms `majority`, `fair`, `drift`
- HVAC controller `preference_estimation`
- annual simulation mode launched from `sim_ep.py`
- control dates `2010-01-01` to `2010-12-30`

## Output

During the full benchmark run, the repository generates:

- `models/temp/temp.idf`
- `results/result_<timestamp>/result-<city>_<algorithm>_<hvac_controller>_<repeat>.txt`

Each result file contains:

- cooling energy in kWh
- heating energy in kWh
- fan energy in kWh
- total energy in kWh
- CO2 value
- ITC
- average ITC
- per-occupant TCE-related values
- standard deviation of TCE-related values

## License

Distributed under the MIT License. See `LICENSE` for details.
