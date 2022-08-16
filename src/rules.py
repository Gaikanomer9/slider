from slo import SLO


def generate_rules(slo: SLO) -> object:
    """Generate from the given SLO object set of Prometheus rules
    """
    print('Mock generated rules: ********************************')
    print(f'Some generated rules for the given SLO {slo.metadata.get("name")}')
    print('Mock generated rules: ********************************')