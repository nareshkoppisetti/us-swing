"""
Agent registry — maps agent_id → agent class.
Lazy-imports each class to avoid circular imports at startup.
"""
import logging
logger = logging.getLogger("agents")

AGENT_REGISTRY = {}

def _load_all():
    """Import all 42 agent classes and register them."""
    from modules.agents.direction.agent_01_regime_detection   import Agent01
    from modules.agents.direction.agent_02_trend_structure    import Agent02
    from modules.agents.direction.agent_03_market_breadth     import Agent03
    from modules.agents.direction.agent_04_market_momentum    import Agent04
    from modules.agents.direction.agent_05_trend_following    import Agent05
    from modules.agents.direction.agent_06_hmm_market_state   import Agent06
    from modules.agents.news_macro.agent_07_news_analyst      import Agent07
    from modules.agents.news_macro.agent_08_earnings_sentiment import Agent08
    from modules.agents.news_macro.agent_09_event_detection   import Agent09
    from modules.agents.news_macro.agent_10_macro_news_impact import Agent10
    from modules.agents.news_macro.agent_11_macro_analyst     import Agent11
    from modules.agents.news_macro.agent_12_federal_reserve   import Agent12
    from modules.agents.news_macro.agent_13_global_liquidity  import Agent13
    from modules.agents.news_macro.agent_14_dollar_strength   import Agent14
    from modules.agents.institutional.agent_15_sector_rotation       import Agent15
    from modules.agents.institutional.agent_16_dark_pool_flow        import Agent16
    from modules.agents.institutional.agent_17_13f_accumulation      import Agent17
    from modules.agents.institutional.agent_18_whale_options_flow    import Agent18
    from modules.agents.institutional.agent_19_insider_transactions  import Agent19
    from modules.agents.institutional.agent_20_etf_flow_intelligence import Agent20
    from modules.agents.strength.agent_21_put_call_parity     import Agent21
    from modules.agents.strength.agent_22_gamma_exposure      import Agent22
    from modules.agents.strength.agent_23_factor_crowding     import Agent23
    from modules.agents.strength.agent_24_uncertainty         import Agent24
    from modules.agents.strength.agent_25_relative_strength   import Agent25
    from modules.agents.strength.agent_26_vix_structure       import Agent26
    from modules.agents.exit_reversal.agent_27_correlation_decay          import Agent27
    from modules.agents.exit_reversal.agent_28_cross_asset_correlation    import Agent28
    from modules.agents.exit_reversal.agent_29_market_leadership          import Agent29
    from modules.agents.prediction_layer.agent_30_signal_aggregation       import Agent30
    from modules.agents.prediction_layer.agent_31_ensemble_model           import Agent31
    from modules.agents.prediction_layer.agent_32_confidence_scoring       import Agent32
    from modules.agents.prediction_layer.agent_33_final_prediction_engine  import Agent33
    from modules.agents.additional.agent_34_oi_structure import Agent34
    from modules.agents.commodity.agent_35_crude_oil              import Agent35
    from modules.agents.commodity.agent_36_gold_precious_metals   import Agent36
    from modules.agents.commodity.agent_37_natural_gas            import Agent37
    from modules.agents.commodity.agent_38_silver                 import Agent38
    from modules.agents.commodity.agent_39_copper                 import Agent39
    from modules.agents.commodity.agent_40_commodity_momentum     import Agent40
    from modules.agents.commodity.agent_41_commodity_sentiment    import Agent41
    from modules.agents.commodity.agent_42_commodity_flow_positioning import Agent42

    classes = [
        Agent01,Agent02,Agent03,Agent04,Agent05,Agent06,
        Agent07,Agent08,Agent09,Agent10,Agent11,Agent12,Agent13,Agent14,
        Agent15,Agent16,Agent17,Agent18,Agent19,Agent20,
        Agent21,Agent22,Agent23,Agent24,Agent25,Agent26,
        Agent27,Agent28,Agent29,
        Agent30,Agent31,Agent32,Agent33,
        Agent34,
        Agent35,Agent36,Agent37,Agent38,Agent39,Agent40,Agent41,Agent42,
    ]
    return {cls.agent_id: cls for cls in classes}


def get_registry() -> dict:
    global AGENT_REGISTRY
    if not AGENT_REGISTRY:
        try:
            AGENT_REGISTRY = _load_all()
            logger.info(f"Agent registry loaded: {len(AGENT_REGISTRY)} agents")
        except Exception as e:
            logger.error(f"Agent registry load failed: {e}")
    return AGENT_REGISTRY


def get_agent(agent_id: int):
    registry = get_registry()
    cls = registry.get(agent_id)
    if cls is None:
        raise KeyError(f"Agent {agent_id} not found in registry")
    return cls()


def list_agents() -> list:
    registry = get_registry()
    out = []
    for agent_id, cls in sorted(registry.items()):
        out.append({
            "agent_id":          cls.agent_id,
            "agent_name":        cls.agent_name,
            "category":          cls.category,
            "refresh_frequency": cls.refresh_frequency,
            "dependencies":      cls.dependencies,
            "tier":              cls.tier,
        })
    return out
