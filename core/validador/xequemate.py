def classificar_sem_lances(ha_lances: bool, em_check: bool) -> str | None:
    if ha_lances:
        return None
    return 'xeque_mate' if em_check else 'afogamento'
