
import pandas as pd

days = range(365)

intervals = [
    "0_0", "0_1", "0_2", "0_3", "0_4", "0_5", "0_6", "0_7", "0_8", "0_9", "0_10",
    "0_11", "0_12", "0_13", "0_14", "0_15", "0_16", "0_17", "0_18", "0_19", "0_20",
    "0_21", "0_22", "0_23"]

d = {'id': [], 'start': [], 'end': []}

cnt = 0
for day in days:
    for interval in intervals:
        start = "PT{}H".format(cnt)
        end = "PT{}H".format(cnt + 1)
        d['id'].append(interval)
        d['start'].append(start)
        d['end'].append(end)

        cnt += 1

df = pd.DataFrame(data=d)

df.to_csv("C:/Users/cenv0553/ED/et_module/data/interval_definitions/daily_intervals.csv", index=False)