"""Doan Van Tai — exact piecewise-linear fluid reference for L1.8A E1 checks.

Assumes constant nonnegative arrival/service rates in every given interval.
This is an analytic reference, not a CTMC fluid solver or packet DES.
"""
from experiments.lessons.l1_2_queue import step


def fluid_interval(q0, rate, service, duration):
    if q0 < 0 or rate < 0 or service < 0 or duration <= 0:
        raise ValueError('q0/rate/service nonnegative; duration positive')
    net = rate-service
    q1 = max(0,q0+net*duration)
    if net < 0 and q0+net*duration < 0:
        area = q0*(q0/(-net))/2
    else:
        area = duration*(q0+q1)/2
    return q1,area


def boundary_comparison(q0, rates, service, dt):
    q = q0
    rows = []
    for k,rate in enumerate(rates):
        end,area = fluid_interval(q,rate,service,dt)
        end_slot,idle = step(q,rate*dt,service*dt)
        assert end == end_slot
        d13 = dt*end
        boundary = dt*(end-q)/2
        rows.append(dict(slot=k,q_start=q,q_end=end,rate_packet_s=rate,service_packet_s=service,
                         fluid_area=area,d13=d13,error=d13-area,boundary_term=boundary,
                         crossing_correction=d13-area-boundary,idle_packet=idle))
        q = end
    return rows
