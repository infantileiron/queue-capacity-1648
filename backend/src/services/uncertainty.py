import math,random,statistics
from src.services.profiling import select_rows,estimate_rates
from src.services.simulation import simulate
# 每组重抽与预演的种子只由(方案seed,组号)派生，与组数无关：增加抽样组数不会改变已有组的样本与结果。
# 全部使用局部random.Random实例，并发分析互不共享随机流；预演种子段与重抽种子段错开，互不串样本。
STRIDE=1000003
def input_uncertainty(rows,profile,scenario):
 sample=select_rows(rows,profile.period)
 if len(sample)<20:raise ValueError("所选时段至少需要20条观测")
 n=len(sample);count=scenario.resamples;groups=[]
 for index in range(count):
  draw=random.Random(scenario.seed*STRIDE+index).choices(sample,k=n)
  fitted=estimate_rates(draw)
  arrival=fitted["arrival_rate"]*scenario.arrival_multiplier;service=fitted["service_rate"]*scenario.service_multiplier
  rho=arrival/(scenario.windows*service)
  rehearsal=simulate(arrival,service,scenario.windows,scenario.duration_minutes,scenario.warmup_minutes,scenario.replications,scenario.seed*STRIDE+500000+index)
  waits=[r["mean_wait_minutes"] for r in rehearsal["replications"]]
  groups.append({"group":index+1,"n":n,"sample_checksum":fitted["statistics"]["checksum"],"sample_preview":[r["sample_id"] for r in draw[:8]],"arrival_rate":fitted["arrival_rate"],"service_rate":fitted["service_rate"],"rho":rho,"stable":rho<1,"mean_wait_minutes":rehearsal["mean_wait_minutes"],"wait_ci95":rehearsal["mean_wait_ci95"],"replication_sd":statistics.stdev(waits)})
 stable=[g for g in groups if g["stable"]]
 summary={"groups":count,"period":profile.period,"seed":scenario.seed,"replications_per_group":scenario.replications,"sample_size":n,"overload":{"groups":count-len(stable),"fraction":(count-len(stable))/count},"stable":None,"groups_detail":groups,"method":"每组按剖面时段整条有放回重抽n条，重估λ/μ并套用方案倍率后独立预演；组间标准差含样本差异与预演噪声，input_sd为扣除组内预演噪声后的样本差异分量。稳定组区间为组均值±1.96×组间标准差（正态近似）；ρ≥1的过载组单列占比，不并入稳定组等待区间。每组种子仅由方案seed与组号派生，与组数无关。"}
 if stable:
  means=[g["mean_wait_minutes"] for g in stable];m=statistics.mean(means)
  between=statistics.stdev(means) if len(stable)>1 else 0.0
  within=math.sqrt(statistics.mean((g["replication_sd"]/math.sqrt(scenario.replications))**2 for g in stable))
  summary["stable"]={"groups":len(stable),"mean_wait_minutes":m,"wait_ci95":[max(0,m-1.96*between),m+1.96*between],"between_group_sd":between,"within_group_sd":within,"input_sd":math.sqrt(max(0,between**2-within**2))}
 return summary
