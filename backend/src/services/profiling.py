import statistics,hashlib,json
def select_rows(rows,period):return [r for r in rows if period=="all" or r["period"]==period]
def estimate_rates(sample):
 arrivals=[r["interarrival_minutes"] for r in sample];services=[r["service_minutes"] for r in sample]
 a=statistics.mean(arrivals);s=statistics.mean(services)
 return {"arrival_rate":1/a,"service_rate":1/s,"statistics":{"n":len(sample),"mean_interarrival":a,"mean_service":s,"interarrival_cv":statistics.stdev(arrivals)/a,"service_cv":statistics.stdev(services)/s,"checksum":hashlib.sha256(json.dumps(sample,sort_keys=True).encode()).hexdigest()}}
def fit_profile(rows,period):
 sample=select_rows(rows,period)
 if len(sample)<20: raise ValueError("所选时段至少需要20条观测")
 return estimate_rates(sample)
