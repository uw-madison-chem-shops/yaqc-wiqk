# namespace "magic"

from . import continuous_flow

continuous_flow = continuous_flow.run

from . import flush

flush = flush.run

from . import refill

refill = refill.run

from . import stopped_flow

stopped_flow = stopped_flow.run
