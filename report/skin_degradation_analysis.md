# Skin Degradation Exploratory Data Analysis

This report summarizes the findings from the `eda.ipynb` analysis regarding skin conditions based on indoor and outdoor environmental tracking. 

The analysis was strictly separated via time-slicing into two contexts:
1. **Long Time Indoor**: Evaluating how the indoor environment impacts the baseline index of the skin before leaving the house.
2. **Long Time Outdoor**: Using the environmental shock and outdoor weather factors to predict skin degradation *after* going out.

---

## 1. Long Time Indoor (Environment Before Going Out)
*The indoor environment was assessed from the start of the day until the moment the person went outside.*

* **Top factor affecting Indoor Water** (Higher is better):  
  - **`in_humidity_max` (+0.37 correlation)**: Reaching high indoor humidity limits significantly helped the skin maintain a higher baseline water level before stepping outside.  
  - Conversely, high indoor temperatures (`in_temp_mean` -0.52 correlation) dried the skin out significantly.
* **Top factor affecting Indoor Oil** (Higher is worse):  
  - **`in_humidity_max` (+0.38 correlation)**: The catch with higher baseline humidity indoors is that while it protects water, it explicitly elevates baseline oil levels before leaving the house.
  - Higher indoor temperatures, conversely, *prevented* baseline oil growth (`in_temp_mean` -0.28 correlation).

---

## 2. Long Time Outdoor (Change after being Outside)
*The outdoor environment was analyzed strictly using timestamps from when the person left the house to when they returned.* 

### Outdoor Degradation Drivers
* **Top factors causing Outdoor Water Decrease** (Negative difference):
  - **`before_water` and `before_oil` (-0.87 correlation)**: The "Spring Back" effect. The higher the initial levels, the more significantly the skin loses water outside rapidly.
  - **`out_cloudCover_mean` (-0.51 correlation)**: Heavily clouded days during the actual trip significantly drove water levels down.
* **Top factors causing Outdoor Oil Increase** (Worse):
  - **`out_uvIndex_max` (+0.31 correlation)**: Peak sun exposure during the exact time outside drove up oil.
  - **`humidity_diff_out_in` (+0.10 correlation)**: The Humidity Shock. Moving from a less humid indoor environment to a more humid outdoor environment directly caused the skin to get oilier.

### Environmental Shock Impact (Out - In Differences)
* **Temperature Shock**: Entering a radically hotter outdoor environment hurt the overall skin balance. It yielded negative correlations on all 3 indices, meaning a larger thermal shock drove slight water loss, elasticity loss, and faster oil generation (decrease in protection).
* **Humidity Shock**: When the person stepped into an environment *more humid* than their house, their **elasticity actually increased** (`+0.30` correlation with elasticity change), but they unfortunately also **generated more oil** (`+0.10` correlation with oil change). Humidity shock did not seem to significantly hurt or preserve overall water levels (`+0.002`).
