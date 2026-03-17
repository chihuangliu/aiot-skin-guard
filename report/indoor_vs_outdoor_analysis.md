# Indoor vs Outdoor Environment Analysis

This report summarizes the findings from the `eda_in_out.ipynb` analysis regarding the temporal relationship and correlation between indoor tracking sensors and outdoor weather API data.

---

## 1. Environmental Time Lag
Peak environmental shifts happen at a noticeable time delay. 

* **Temperature Lag**: It takes an average of **9 hours** for the maximum correlation (0.599) between outdoor temperature and indoor temperature to register. This indicates that the building effectively slows down thermal shock, possibly via insulation or internal climate controls.
* **Humidity Lag**: Indoor humidity reacts much swifter. The peak correlation (0.516) against changing outdoor humidity is established within just a **2-hour delay**.

## 2. Direct Outdoor Influencers on Indoor Conditions

### Drivers of Indoor Humidity
Indoor Humidity is strongly dictated by outdoor wind and humidity:
* **`out_humidity`**: Strongest positive correlator (+0.50). 
* **`out_windSpeed`**: Strongest *negative* correlator against indoor humidity (-0.51). Windier days correlate powerfully with drier indoor air, suggesting wind strips out moisture quickly.

### Drivers of Indoor Temperature
Indoor temperature behaves more sluggishly to immediate outdoor conditions, largely shielded by the 9-hour thermal lag:
* The highest immediate influencers on indoor temperature are **`out_dewPoint`** (+0.38) and **`out_temperature`** (+0.32).
* Due to the 9-hour latency, instantaneous measurements do not yield a perfectly matched correlation score, as the internal environment actively resists immediate external thermal shocks.
