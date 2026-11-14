from src.services.erlang import erlang_c
from src.services.simulation import simulate
from src.services.uncertainty import input_uncertainty
def analyze(profile,scenario,rows=None):
 arrival=profile.arrival_rate*scenario.arrival_multiplier;service=profile.service_rate*scenario.service_multiplier
 analytic=erlang_c(arrival,service,scenario.windows)
 simulation=simulate(arrival,service,scenario.windows,scenario.duration_minutes,scenario.warmup_minutes,scenario.replications,scenario.seed)
 result={"analytic":analytic,"simulation":simulation,"comparison":[erlang_c(arrival,service,c) for c in sorted({2,3,4,scenario.windows})],"profile_statistics":profile.statistics,"assumptions":["所有率均为每分钟；μ是每个窗口的服务率。理论要求泊松到达、独立指数服务、同质窗口、无限等候空间及稳态。","观测按时段估计均值；聚合高峰与平峰不保证泊松稳态。CV偏离1提示指数假设可能不符。","仿真从空系统开始，先warmup后统计观测期到达，服务可延续到观察结束之后。warmup只能缓解初态影响，不能保证已收敛。","rho≥1没有有限稳态均值；有限期仿真仍会给出暂态等待，不能用于证明稳定。","95%区间量化固定模型下重复仿真误差，不含输入率估计误差。"]}
 if (getattr(scenario,"resamples",0) or 0)>=2:
  if rows is None:raise ValueError("输入不确定性分析需要观测样本")
  result["input_uncertainty"]=input_uncertainty(rows,profile,scenario)
  result["assumptions"]+=["输入不确定性：按剖面时段整条重抽样本，每组重估λ/μ并多次预演；组间样本差异与组内预演波动分列，ρ≥1的重抽组单列占比，不并入稳定组等待区间。"]
 return result
